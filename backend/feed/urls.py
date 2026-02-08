from django.urls import path
from .views import (
    PostListView, PostDetailView, LikePostView, LikeCommentView, 
    LeaderboardView, CommentCreateView, RegisterView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', LikePostView.as_view(), name='post-like'),
    path('posts/<int:pk>/comments/', CommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/like/', LikeCommentView.as_view(), name='comment-like'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
