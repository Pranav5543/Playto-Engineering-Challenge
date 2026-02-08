import os
import django
import random
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from feed.models import Post, Comment, PostLike, CommentLike

def seed():
    # 1. Create Users
    users = []
    for i in range(1, 6):
        username = f'user{i}'
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password('pass123')
            user.save()
        users.append(user)

    # 2. Create Posts
    posts = []
    for i in range(1, 4):
        post = Post.objects.create(
            author=random.choice(users),
            content=f'This is post number {i}. Community feed in action!'
        )
        posts.append(post)

    # 3. Create Comments (Threaded)
    for post in posts:
        # Top level comments
        for i in range(1, 3):
            c1 = Comment.objects.create(
                author=random.choice(users),
                post=post,
                content=f'Top level comment {i} on post {post.id}'
            )
            # Replies
            for j in range(1, 3):
                c2 = Comment.objects.create(
                    author=random.choice(users),
                    post=post,
                    parent=c1,
                    content=f'Reply {j} to comment {c1.id}'
                )
                # Deep nested reply
                Comment.objects.create(
                    author=random.choice(users),
                    post=post,
                    parent=c2,
                    content=f'Deep nested reply to {c2.id}'
                )

    # 4. Create Likes (Last 24h for leaderboard)
    # Some older likes to test dynamic 24h window
    old_time = timezone.now() - timedelta(days=2)
    
    for post in posts:
        # Recent likes
        for user in random.sample(users, k=3):
            PostLike.objects.get_or_create(user=user, post=post)
        
    for comment in Comment.objects.all():
        # Random likes
        for user in random.sample(users, k=random.randint(0, 3)):
            CommentLike.objects.get_or_create(user=user, comment=comment)

    print("Seeding complete!")

if __name__ == '__main__':
    seed()
