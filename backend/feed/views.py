from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Count, Q, F, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Post, Comment, PostLike, CommentLike
from .serializers import (
    PostSerializer, CommentSerializer, UserSerializer, LeaderboardSerializer
)
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username}, status=status.HTTP_201_CREATED)

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    ).order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context['liked_post_ids'] = set(
                PostLike.objects.filter(user=self.request.user).values_list('post_id', flat=True)
            )
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    )
    serializer_class = PostSerializer

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        
        # N+1 Nightmare Solution:
        # 1. Fetch all comments for this post in a single query with author data.
        comments = Comment.objects.filter(post=post).select_related('author').annotate(
            likes_count=Count('likes', distinct=True)
        ).order_by('created_at')
        
        # 2. Build a map of parent_id -> [children]
        all_comments_map = {}
        for comment in comments:
            parent_id = comment.parent_id
            if parent_id not in all_comments_map:
                all_comments_map[parent_id] = []
            all_comments_map[parent_id].append(comment)
        
        # 3. Get liked comment IDs for the user
        liked_comment_ids = set()
        if request.user.is_authenticated:
            liked_comment_ids = set(
                CommentLike.objects.filter(user=request.user, comment__post=post).values_list('comment_id', flat=True)
            )
        
        # 4. Serialize top-level comments (parent=None)
        context = {
            'request': request,
            'all_comments_map': all_comments_map,
            'liked_comment_ids': liked_comment_ids
        }
        
        top_level_comments = all_comments_map.get(None, [])
        post_data = self.get_serializer(post, context=self.get_serializer_context()).data
        post_data['comments'] = CommentSerializer(top_level_comments, many=True, context=context).data
        
        return Response(post_data)

class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        # Handle Race Condition with get_or_create or atomic transaction
        with transaction.atomic():
            like, created = PostLike.objects.get_or_create(user=request.user, post=post)
            if not created:
                # If already liked, then unlike (toggle behavior)
                like.delete()
                return Response({'liked': False}, status=status.HTTP_200_OK)
            
        return Response({'liked': True}, status=status.HTTP_201_CREATED)

class LikeCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        with transaction.atomic():
            like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
            if not created:
                like.delete()
                return Response({'liked': False}, status=status.HTTP_200_OK)
                
        return Response({'liked': True}, status=status.HTTP_201_CREATED)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_id)
        parent_id = self.request.data.get('parent')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id)
        serializer.save(author=self.request.user, post=post, parent=parent)

class LeaderboardView(APIView):
    def get(self, request):
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        
        # The Math: Dynamically calculate karma from last 24h likes
        leaderboard = User.objects.annotate(
            post_karma=Coalesce(
                Count('posts__likes', filter=Q(posts__likes__created_at__gte=twenty_four_hours_ago), distinct=True),
                0, output_field=IntegerField()
            ) * 5,
            comment_karma=Coalesce(
                Count('comments__likes', filter=Q(comments__likes__created_at__gte=twenty_four_hours_ago), distinct=True),
                0, output_field=IntegerField()
            ) * 1
        ).annotate(
            karma=F('post_karma') + F('comment_karma')
        ).filter(karma__gt=0).order_by('-karma')[:5]
        
        data = LeaderboardSerializer(leaderboard, many=True).data
        return Response(data)
