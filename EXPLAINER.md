# technical Explainer

### 1. The Tree: Nested Comments
**Modeling**: I used a self-referential `ForeignKey` on the `Comment` model: `parent = models.ForeignKey('self', ...)` to represent the parent-child relationship.

**Serialization (The N+1 Nightmare Solution)**: 
The biggest challenge with nested comments is the recursive "N+1" problem, where fetching 50 nested comments triggers 50 separate SQL queries. To solve this:
- I fetched all comments for a post in a **single query** using `.select_related('author')` and `.annotate(likes_count=Count('likes'))`.
- In the view, I built a `all_comments_map` (parent_id -> [children]).
- I passed this map into the Serializer context.
- The `CommentSerializer` then filters from this in-memory list instead of hitting the database again for each child level. 
- This ensures that no matter how deep the tree is, the database is only hit **once** for comments.

### 2. The Math: 24h Leaderboard
The leaderboard calculates karma dynamically from activity in the last 24 hours. No static "daily karma" field is used.

**QuerySet**:
```python
twenty_four_hours_ago = timezone.now() - timedelta(hours=24)

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
```

### 3. The Modern Stack: Tailwind v4 Upgrade
During the build, I encountered a PostCSS integration error because Tailwind CSS v4 was recently released and changed its architectural approach.
- **The Problem**: Tailwind v4 no longer uses `tailwindcss` as a direct PostCSS plugin in the traditional way; it now offers a native Vite plugin.
- **The Solution**: I refactored the frontend to use the `@tailwindcss/vite` plugin and migrated styles to the new CSS-first configuration in `index.css`. This ensures the project uses the latest, most performant version of Tailwind.

### 4. The AI Audit
**The Bug**: During the initial generation of the `LeaderboardView`, the AI suggested using a simple `Sum` on a related field across multiple branches (Posts and Comments) without using `distinct=True` in the counts. 
**The Issue**: This causes a "join explosion" (Cartesian product issue), where the counts of likes on posts would be multiplied by the counts of likes on comments for the same user, resulting in astronomically high and incorrect karma numbers.
**The Fix**: I manually added `distinct=True` to both `Count` aggregations and used `Coalesce` to handle cases where a user might have 0 likes in one category, ensuring the addition `F('post_karma') + F('comment_karma')` doesn't result in `NULL`.

### 5. Backend Stability: The "AttributeError" Fix
During testing, I discovered an `AttributeError: 'Post' object has no setter` when accessing the post feed.
- **The Culprit**: The `Post` model had a read-only `@property` for `likes_count`. Simultaneously, the `PostListView` was trying to use Django's `.annotate(likes_count=...)`.
- **The Conflict**: Django's `annotate` needs to dynamically set the `likes_count` attribute on the model instance. Because a read-only property of the same name existed, the assignment failed.
- **The Fix**: I removed the redundant model properties and moved all count logic to QuerySet annotations. This resolved the crash and improved efficiency by offloading calculations to the database.
