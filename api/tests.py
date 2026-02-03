from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Post, Comment, Vote
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

class LeaderboardTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='alice', password='password')
        self.user2 = User.objects.create_user(username='bob', password='password')
        self.user3 = User.objects.create_user(username='charlie', password='password')

        # Alice creates a post
        self.post1 = Post.objects.create(author=self.user1, content="Alice's post")
        
        # Bob creates a comment on Alice's post
        self.comment1 = Comment.objects.create(author=self.user2, post=self.post1, content="Bob's comment")

        # Content Types
        self.post_ct = ContentType.objects.get_for_model(Post)
        self.comment_ct = ContentType.objects.get_for_model(Comment)

    def test_leaderboard_logic(self):
        # Scenario:
        # 1. Charlie likes Alice's post (within 24h) -> Alice +5
        # 2. Charlie likes Bob's comment (within 24h) -> Bob +1
        # 3. Bob likes Alice's post (OLD, >24h) -> Alice +0
        
        # 1. Charlie likes Alice's post (Now)
        Vote.objects.create(
            user=self.user3,
            content_type=self.post_ct,
            object_id=self.post1.id,
            value=1
        )
        
        # 2. Charlie likes Bob's comment (Now)
        Vote.objects.create(
            user=self.user3,
            content_type=self.comment_ct,
            object_id=self.comment1.id,
            value=1
        )
        
        # 3. Bob likes Alice's post (25 hours ago)
        old_time = timezone.now() - timedelta(hours=25)
        v = Vote.objects.create(
            user=self.user2,
            content_type=self.post_ct,
            object_id=self.post1.id,
            value=1
        )
        v.created_at = old_time
        v.save()
        
        # Check Leaderboard
        url = reverse('leaderboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Expected: 
        # Alice: 5 points (1 post like recent)
        # Bob: 1 point (1 comment like recent)
        # Charlie: 0 points
        
        # Only top users returned?
        # data list of {username, score}
        
        # Verify Alice
        alice_entry = next((item for item in data if item['username'] == 'alice'), None)
        self.assertIsNotNone(alice_entry)
        self.assertEqual(alice_entry['score'], 5)
        
        # Verify Bob
        bob_entry = next((item for item in data if item['username'] == 'bob'), None)
        self.assertIsNotNone(bob_entry)
        self.assertEqual(bob_entry['score'], 1)
        
        # Verify Charlie (Score 0, might not be in list if we filter, currently my implementation fetches valid users with scores > 0? No, my implementation fetches top 5 of *all* users who have votes? 
        # Wait, my implementation iterates over `post_karma` and `comment_karma`.
        # If user has no votes in 24h, they are not in the dict.
        # So Charlie shouldn't be there or score 0 if implied.
        # My map `scores` only has authors from queries.
        
        charlie_entry = next((item for item in data if item['username'] == 'charlie'), None)
        self.assertIsNone(charlie_entry) # Should be None as he earned 0

    def test_recursive_comments(self):
        # Test tree building
        # Alice: Post
        #   Bob: Comment 1
        #     Charlie: Reply to Comment 1
        
        reply = Comment.objects.create(
            author=self.user3,
            post=self.post1,
            parent=self.comment1,
            content="Charlie's reply"
        )
        
        url = reverse('post-detail', args=[self.post1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check comments structure
        self.assertEqual(len(data['comments']), 1) # Top level: Bob's comment
        bobs_comment = data['comments'][0]
        self.assertEqual(bobs_comment['content'], "Bob's comment")
        
        self.assertEqual(len(bobs_comment['replies']), 1)
        charlies_reply = bobs_comment['replies'][0]
        self.assertEqual(charlies_reply['content'], "Charlie's reply")
