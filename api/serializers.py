from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Vote
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    user_has_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'parent', 'replies', 'likes_count', 'user_has_liked', 'post']

    def get_replies(self, obj):
        # Expects 'prefetched_replies' to be set on the object by the view/builder to avoid N+1
        if hasattr(obj, 'prefetched_replies'):
            return CommentSerializer(obj.prefetched_replies, many=True).data
        return []

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    user_has_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes_count', 'user_has_liked']

class PostDetailSerializer(PostSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']

    def get_comments(self, obj):
        # Expects 'prefetched_comments' (top-level comments) to be set on the object
        if hasattr(obj, 'prefetched_comments'):
            return CommentSerializer(obj.prefetched_comments, many=True).data
        return []

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'value']

class LeaderboardEntrySerializer(serializers.Serializer):
    username = serializers.CharField()
    score = serializers.IntegerField()
