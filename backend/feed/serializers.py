from rest_framework import serializers
from .models import Post, Comment, PostLike, CommentLike
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    post = serializers.PrimaryKeyRelatedField(read_only=True)
    parent_author = serializers.CharField(source='parent.author.username', read_only=True, allow_null=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'post', 'parent', 'parent_author', 'content', 'created_at', 'likes_count', 'is_liked', 'replies']

    def get_likes_count(self, obj):
        return getattr(obj, 'likes_count', 0)

    def get_replies(self, obj):
        all_comments = self.context.get('all_comments_map')
        if all_comments and obj.id in all_comments:
            return CommentSerializer(all_comments[obj.id], many=True, context=self.context).data
        return []

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            liked_comment_ids = self.context.get('liked_comment_ids', set())
            return obj.id in liked_comment_ids
        return False

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes_count', 'is_liked', 'comments_count']

    def get_likes_count(self, obj):
        return getattr(obj, 'likes_count', 0)

    def get_comments_count(self, obj):
        return getattr(obj, 'comments_count', 0)

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            liked_post_ids = self.context.get('liked_post_ids', set())
            return obj.id in liked_post_ids
        return False

class LeaderboardSerializer(serializers.Serializer):
    username = serializers.CharField()
    karma = serializers.IntegerField()
