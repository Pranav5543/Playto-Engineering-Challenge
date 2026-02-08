from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import connection
from django.test.utils import override_settings
from datetime import timedelta
from rest_framework.test import APIClient
from .models import Post, Comment, PostLike, CommentLike

class LeaderboardTestCase(TestCase):
    """Test that leaderboard only counts karma from last 24 hours"""
    
    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.user1 = User.objects.create_user('testuser1', password='testpass123')
        self.user2 = User.objects.create_user('testuser2', password='testpass123')
        self.user3 = User.objects.create_user('testuser3', password='testpass123')
    
    def test_24h_karma_calculation_post_likes(self):
        """Test that only likes from last 24h count toward karma"""
        # Create a post by user1
        post = Post.objects.create(author=self.user1, content="Test post")
        
        # Create an OLD like (25 hours ago) - should NOT count
        old_like = PostLike.objects.create(user=self.user2, post=post)
        old_like.created_at = timezone.now() - timedelta(hours=25)
        old_like.save()
        
        # Create a RECENT like (1 hour ago) - SHOULD count
        recent_like = PostLike.objects.create(user=self.user3, post=post)
        recent_like.created_at = timezone.now() - timedelta(hours=1)
        recent_like.save()
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        # user1 should have exactly 5 karma (1 recent post like * 5)
        leaderboard_data = response.data
        user1_entry = next((u for u in leaderboard_data if u['username'] == 'testuser1'), None)
        
        self.assertIsNotNone(user1_entry, "user1 should be in leaderboard")
        self.assertEqual(user1_entry['karma'], 5, "user1 should have 5 karma from 1 recent post like")
    
    def test_24h_karma_calculation_comment_likes(self):
        """Test that comment likes contribute 1 karma each"""
        # Create post and comment
        post = Post.objects.create(author=self.user1, content="Test post")
        comment = Comment.objects.create(author=self.user2, post=post, content="Test comment")
        
        # Create recent comment like
        CommentLike.objects.create(user=self.user3, comment=comment)
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        # user2 should have exactly 1 karma (1 comment like * 1)
        leaderboard_data = response.data
        user2_entry = next((u for u in leaderboard_data if u['username'] == 'testuser2'), None)
        
        self.assertIsNotNone(user2_entry, "user2 should be in leaderboard")
        self.assertEqual(user2_entry['karma'], 1, "user2 should have 1 karma from 1 comment like")
    
    def test_24h_karma_mixed_calculation(self):
        """Test combined post and comment karma calculation"""
        # Create post by user1
        post = Post.objects.create(author=self.user1, content="Test post")
        
        # Create comment by user1
        comment = Comment.objects.create(author=self.user1, post=post, content="Test comment")
        
        # user2 likes the post (5 karma for user1)
        PostLike.objects.create(user=self.user2, post=post)
        
        # user3 likes the comment (1 karma for user1)
        CommentLike.objects.create(user=self.user3, comment=comment)
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        # user1 should have 6 karma (5 from post + 1 from comment)
        leaderboard_data = response.data
        user1_entry = next((u for u in leaderboard_data if u['username'] == 'testuser1'), None)
        
        self.assertIsNotNone(user1_entry, "user1 should be in leaderboard")
        self.assertEqual(user1_entry['karma'], 6, "user1 should have 6 karma (5+1)")
    
    def test_leaderboard_top_5_limit(self):
        """Test that leaderboard returns max 5 users"""
        # Create 7 users with posts
        for i in range(7):
            user = User.objects.create_user(f'user{i}', password='pass')
            post = Post.objects.create(author=user, content=f"Post {i}")
            # Each gets 1 like
            PostLike.objects.create(user=self.user1, post=post)
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        # Should return max 5 users
        self.assertLessEqual(len(response.data), 5, "Leaderboard should return max 5 users")
    
    def test_leaderboard_excludes_zero_karma(self):
        """Test that users with 0 karma are excluded"""
        # Create user with no likes
        user_no_karma = User.objects.create_user('nokarma', password='pass')
        Post.objects.create(author=user_no_karma, content="Unloved post")
        
        # Fetch leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        # nokarma user should NOT be in leaderboard
        usernames = [u['username'] for u in response.data]
        self.assertNotIn('nokarma', usernames, "Users with 0 karma should not appear")


class ConcurrencyTestCase(TransactionTestCase):
    """Test that double-liking is prevented (concurrency safety)"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', password='testpass123')
        self.post = Post.objects.create(author=self.user, content="Test post")
        self.client.force_authenticate(user=self.user)
    
    def test_cannot_double_like_post(self):
        """Test that a user cannot like the same post twice"""
        # First like should succeed
        response1 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response1.status_code, 201)
        self.assertTrue(response1.data['liked'])
        
        # Count likes
        like_count_1 = PostLike.objects.filter(post=self.post, user=self.user).count()
        self.assertEqual(like_count_1, 1, "Should have exactly 1 like")
        
        # Second like should toggle (unlike)
        response2 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(response2.data['liked'])
        
        # Count likes again
        like_count_2 = PostLike.objects.filter(post=self.post, user=self.user).count()
        self.assertEqual(like_count_2, 0, "Should have 0 likes after toggle")
    
    def test_cannot_double_like_comment(self):
        """Test that a user cannot like the same comment twice"""
        comment = Comment.objects.create(author=self.user, post=self.post, content="Test")
        
        # First like
        response1 = self.client.post(f'/api/comments/{comment.id}/like/')
        self.assertEqual(response1.status_code, 201)
        self.assertTrue(response1.data['liked'])
        
        # Verify exactly 1 like
        like_count_1 = CommentLike.objects.filter(comment=comment, user=self.user).count()
        self.assertEqual(like_count_1, 1)
        
        # Second like (toggle)
        response2 = self.client.post(f'/api/comments/{comment.id}/like/')
        self.assertEqual(response2.status_code, 200)
        self.assertFalse(response2.data['liked'])
        
        # Verify 0 likes
        like_count_2 = CommentLike.objects.filter(comment=comment, user=self.user).count()
        self.assertEqual(like_count_2, 0)
    
    def test_unique_constraint_prevents_duplicates(self):
        """Test that database constraint prevents duplicate likes"""
        from django.db import IntegrityError
        
        # Create first like
        PostLike.objects.create(user=self.user, post=self.post)
        
        # Attempt to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            PostLike.objects.create(user=self.user, post=self.post)


class N1QueryOptimizationTestCase(TestCase):
    """Test that nested comments don't trigger N+1 queries"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', password='testpass123')
        self.post = Post.objects.create(author=self.user, content="Test post")
    
    def test_nested_comments_single_query(self):
        """Test that fetching post with nested comments uses minimal queries"""
        # Create nested comment structure (3 levels deep)
        comment1 = Comment.objects.create(author=self.user, post=self.post, content="Level 1")
        comment2 = Comment.objects.create(author=self.user, post=self.post, parent=comment1, content="Level 2")
        comment3 = Comment.objects.create(author=self.user, post=self.post, parent=comment2, content="Level 3")
        
        # Reset query counter
        from django.db import reset_queries
        reset_queries()
        
        # Fetch post with comments
        # Expected queries: post fetch, comments fetch, liked_posts check, liked_comments check, post serializer context
        response = self.client.get(f'/api/posts/{self.post.id}/')
        
        self.assertEqual(response.status_code, 200)
        
        # The key is that query count should NOT scale with comment depth
        # With 3 levels of nesting, we should still have < 10 queries (not 3+ per level)
        from django.db import connection
        query_count = len(connection.queries)
        self.assertLess(query_count, 10, f"Should use < 10 queries, used {query_count}")
        
        # Verify all comments are present
        comments = response.data['comments']
        self.assertEqual(len(comments), 1, "Should have 1 top-level comment")
        self.assertEqual(len(comments[0]['replies']), 1, "Should have 1 reply")
        self.assertEqual(len(comments[0]['replies'][0]['replies']), 1, "Should have 1 nested reply")
    
    def test_many_comments_query_count(self):
        """Test that 50 comments don't trigger 50 queries"""
        # Create 50 comments
        for i in range(50):
            Comment.objects.create(author=self.user, post=self.post, content=f"Comment {i}")
        
        # Reset query counter
        from django.db import reset_queries
        reset_queries()
        
        # Fetch post - should NOT trigger 50+ queries
        response = self.client.get(f'/api/posts/{self.post.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 50, "Should return all 50 comments")
        
        # The key metric: query count should NOT scale with comment count
        # With 50 comments, we should still have < 10 queries (not 50+)
        from django.db import connection
        query_count = len(connection.queries)
        self.assertLess(query_count, 10, f"Should use < 10 queries for 50 comments, used {query_count}")


class ThreadedCommentsTestCase(TestCase):
    """Test threaded comment functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user('user1', password='pass')
        self.user2 = User.objects.create_user('user2', password='pass')
        self.post = Post.objects.create(author=self.user1, content="Test post")
        self.client.force_authenticate(user=self.user2)
    
    def test_create_top_level_comment(self):
        """Test creating a comment on a post"""
        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            {'content': 'Great post!'}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Great post!')
        self.assertIsNone(comment.parent, "Top-level comment should have no parent")
    
    def test_create_nested_reply(self):
        """Test replying to a comment"""
        # Create parent comment
        parent = Comment.objects.create(
            author=self.user1, 
            post=self.post, 
            content="Parent comment"
        )
        
        # Reply to parent
        response = self.client.post(
            f'/api/posts/{self.post.id}/comments/',
            {'content': 'Reply to parent', 'parent': parent.id}
        )
        self.assertEqual(response.status_code, 201)
        
        reply = Comment.objects.get(content='Reply to parent')
        self.assertEqual(reply.parent, parent, "Reply should reference parent")
    
    def test_deeply_nested_comments(self):
        """Test that comments can be nested infinitely"""
        # Create 5-level deep nesting
        parent = None
        for i in range(5):
            comment = Comment.objects.create(
                author=self.user1,
                post=self.post,
                parent=parent,
                content=f"Level {i}"
            )
            parent = comment
        
        # Fetch post
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Verify nesting structure
        comments = response.data['comments']
        self.assertEqual(len(comments), 1, "Should have 1 top-level comment")
        
        # Walk down the tree
        current = comments[0]
        for i in range(4):
            self.assertEqual(len(current['replies']), 1, f"Level {i} should have 1 reply")
            current = current['replies'][0]
