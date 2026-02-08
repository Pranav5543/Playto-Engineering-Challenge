import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from feed.models import Post
from feed.serializers import PostSerializer
from django.db.models import Count
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/')

posts = Post.objects.annotate(
    likes_count=Count('likes', distinct=True),
    comments_count=Count('comments', distinct=True)
)

print(f"Number of posts: {posts.count()}")
if posts.exists():
    p = posts.first()
    print(f"Post ID: {p.id}")
    print(f"Likes Count (attr): {getattr(p, 'likes_count', 'MISSING')}")
    print(f"Comments Count (attr): {getattr(p, 'comments_count', 'MISSING')}")
    
    serializer = PostSerializer(p, context={'request': request})
    try:
        print("Serializing...")
        print(serializer.data)
    except Exception as e:
        print(f"Serialization Error: {e}")
else:
    print("No posts found.")
