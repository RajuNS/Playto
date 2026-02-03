from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, VoteView, LeaderboardView

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('vote/<str:model_name>/<int:pk>/', VoteView.as_view(), name='vote'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
