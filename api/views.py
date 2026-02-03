from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count, Exists, OuterRef, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import Post, Comment, Vote
from django.contrib.auth import get_user_model
from .serializers import (
    PostSerializer, PostDetailSerializer, CommentSerializer,
    LeaderboardEntrySerializer, UserSerializer
)

User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset().select_related('author')
        
        # Annotate likes count
        qs = qs.annotate(likes_count=Count('votes'))
        
        # Annotate user_has_liked
        if user.is_authenticated:
            post_ct = ContentType.objects.get_for_model(Post)
            likes = Vote.objects.filter(
                content_type=post_ct,
                object_id=OuterRef('pk'),
                user=user
            )
            qs = qs.annotate(user_has_liked=Exists(likes))
        else:
            qs = qs.annotate(user_has_liked=Exists(Post.objects.none()))
            
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Fetch all comments for this post in constant queries
        # 1 query for comments
        # 1 query for User (author) - handled by select_related
        # 1 query for Vote counts - handled by annotation
        # 1 query for User Vote status - handled by annotation
        
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        comments_qs = Comment.objects.filter(post=instance).select_related('author')
        comments_qs = comments_qs.annotate(likes_count=Count('votes'))
        
        if request.user.is_authenticated:
            user_likes = Vote.objects.filter(
                content_type=comment_ct,
                object_id=OuterRef('pk'),
                user=request.user
            )
            comments_qs = comments_qs.annotate(user_has_liked=Exists(user_likes))
        else:
            comments_qs = comments_qs.annotate(user_has_liked=Exists(Comment.objects.none()))

        # Execute query
        all_comments = list(comments_qs)
        
        # Build tree in memory
        comment_map = {c.id: c for c in all_comments}
        top_level_comments = []
        
        for comment in all_comments:
            comment.prefetched_replies = [] # Initialize empty list for recursive serializer
        
        for comment in all_comments:
            if comment.parent_id:
                parent = comment_map.get(comment.parent_id)
                if parent:
                    parent.prefetched_replies.append(comment)
            else:
                top_level_comments.append(comment)
                
        instance.prefetched_comments = top_level_comments
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class VoteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request, model_name, pk):
        # 'model_name' should be 'post' or 'comment'
        if model_name.lower() == 'post':
            model = Post
        elif model_name.lower() == 'comment':
            model = Comment
        else:
            return Response({'error': 'Invalid model'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            obj = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
            
        ct = ContentType.objects.get_for_model(model)
        
        # Concurrency: Use atomic transaction
        # To strictly prevent double-likes even with race conditions, DB unique constraint is key.
        # We have UniqueConstraint(user, content_type, object_id) in Vote model.
        
        try:
            Vote.objects.create(
                user=request.user,
                content_type=ct,
                object_id=obj.pk,
                value=1
            )
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
        except Exception: # IntegrityError
            # If already liked, we can unlike (toggle) or return error. 
            # Requirement says "cannot double like". It implies state check.
            # Let's verify if they want toggle or explicit Unlike.
            # "Like/Unlike API" in task list implies both.
            # Let's check if it exists and delete.
            deleted, _ = Vote.objects.filter(
                user=request.user,
                content_type=ct,
                object_id=obj.pk
            ).delete()
            
            if deleted:
                return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
            else:
               # Should not happen if create failed due to integrity error, 
               # but strictly speaking create might fail for other reasons.
               # If IntegrityError, it meant it existed.
               return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

class LeaderboardView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = LeaderboardEntrySerializer

    def get_queryset(self):
        # Calculate last 24h
        last_24h = timezone.now() - timedelta(hours=24)
        
        # We need to sum up karma for each user.
        # User -> posts -> votes (worth 5)
        # User -> comments -> votes (worth 1)
        
        # To avoid Cartesian products when joining two to-many relationships (posts-votes and comments-votes),
        # we should use subqueries or sum them separately.
        # Given this is a prototype, assuming not huge scale, we can try a combined approach but Django might warn.
        # Better: use Subquery.
        
        post_ct = ContentType.objects.get_for_model(Post)
        comment_ct = ContentType.objects.get_for_model(Comment)
        
        # Subquery for Post Karma
        # We want: for each user, sum(votes on their posts created > 24h) * 5
        # Vote -> GenericFK to Post -> Author
        # Note: GenericRelation on Post is 'votes'.
        
        # Unfortunately, querying backward from User -> Post -> Vote via Subquery is easiest.
        
        # Let's count votes on posts for the user
        # We can filters votes by content_type=post_ct, created_at > 24h.
        # But we need to group by Post__Author.
        # The Vote model has 'object_id'.
        # We can't easily join object_id to Post table inside a Value aggregate without proper setup.
        
        # However, we have GenericRelation.
        # So we can filter Post objects independent of User?
        
        # Let's try the direct annotation and see if Django handles it (it usually does separate subqueries for multiple annotations since Django 2.0+ if strict).
        # Actually, let's just do it in Python for the "Top Users" if the user count is small? No, "complex systems efficienty".
        
        # Correct efficient approach:
        # 1. Aggregation on Votes for Posts
        post_karma_qs = Vote.objects.filter(
            content_type=post_ct,
            created_at__gte=last_24h
        ).values('object_id') # Group by Post
        
        # This gives votes per post. We need votes per Author.
        # We need to join Vote -> Post -> Author.
        
        # Since Vote has GenericForeignKey, we can't directly join 'content_object__author'.
        # Constraints says "The Tree" and "The Math" are important.
        
        # Efficient SQL way:
        # SELECT post.author_id, COUNT(*) * 5 
        # FROM api_vote v 
        # JOIN api_post p ON v.object_id = p.id 
        # WHERE v.content_type_id = <post_ct_id> AND v.created_at >= <date>
        # GROUP BY p.author_id
        
        # We can express this in Django ORM starting from Post?
        # Post.objects.filter(votes__created_at__gte=last_24h).values('author').annotate(k=Count('votes')*5)
        
        post_karma = Post.objects.filter(
            votes__created_at__gte=last_24h,
            votes__content_type=post_ct # Redundant if using related name but safe
        ).values('author').annotate(
            score=Count('votes') * 5
        )
        
        comment_karma = Comment.objects.filter(
            votes__created_at__gte=last_24h,
            votes__content_type=comment_ct
        ).values('author').annotate(
            score=Count('votes')
        )
        
        # Now we have two querysets:
        # [{'author': 1, 'score': 10}, ...]
        # [{'author': 2, 'score': 3}, ...]
        
        # We merge them in Python. For a "Top 5" leaderboard, this is efficient enough 
        # unless we have millions of active users in 24h.
        # If we strictly need SQL, we can use union or common table expressions, 
        # or a User query with Subqueries.
        
        # Let's use Python merge for readability and reasonable performance.
        # To get the User objects, we can extract IDs.
        
        scores = {}
        
        # Convert to dict
        for item in post_karma:
            uid = item['author']
            scores[uid] = scores.get(uid, 0) + item['score']
            
        for item in comment_karma:
            uid = item['author']
            scores[uid] = scores.get(uid, 0) + item['score']
            
        # Sort top 5
        top_user_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Fetch User objects
        results = []
        if top_user_ids:
            users = User.objects.in_bulk([uid for uid, _ in top_user_ids])
            for uid, score in top_user_ids:
                user = users.get(uid)
                if user:
                    results.append({'username': user.username, 'score': score})
                    
        return results

    def list(self, request, *args, **kwargs):
        # Override list to avoid pagination overhead if we return list
        data = self.get_queryset()
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

