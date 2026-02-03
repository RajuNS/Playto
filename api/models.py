from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class User(AbstractUser):
    # We can add an 'avatar' field later if needed, but for now standard django user is fine.
    # Karma could be a field for display efficiency, but requirements strictly say: 
    # "Do not store 'Daily Karma' in a simple integer field... Calculate it dynamically"
    pass

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = GenericRelation('Vote')
    
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    votes = GenericRelation('Vote')

    def __str__(self):
        return f"Comment by {self.author.username}"

class Vote(models.Model):
    # Using a generic relation allows voting on both Post and Comment
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    value = models.IntegerField(default=1) # Always 1 for "Like". Could be -1 for dislike if needed.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'content_type', 'object_id'], name='unique_vote')
        ]
        indexes = [
            models.Index(fields=['created_at']), # For leaderboard filtering
            models.Index(fields=['content_type', 'object_id']), # For lookups
        ]
