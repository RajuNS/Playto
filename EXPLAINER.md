# Explainer

## The Tree (Nested Comments)
To model nested comments, I used the **Adjacency List** pattern where each `Comment` has a `parent` ForeignKey to itself.

### Optimization (Avoiding N+1)
Fetching a post with 50 nested comments could trigger 50 recursive SQL queries if not careful.
I optimized this by fetching **all comments for a post in a single query** and reconstructing the tree in memory (Python).

**Strategy:**
1. Query all comments for the post: `Comment.objects.filter(post=post_id)`.
2. Create a dictionary mapping `id -> comment_object`.
3. Iterate and attach each comment to its parent's `replies` list.
4. Pass the top-level comments to a recursive Serializer.

This ensures that regardless of depth or count, we only execute **1 SQL query** to fetch comments.

## The Math (Leaderboard)
The leaderboard requires calculating Karma earned strictly in the last 24 hours.
- 1 Post Like = 5 Karma
- 1 Comment Like = 1 Karma

I used Django's aggregation with `Count` and filtered by time. To avoid potential Cartesian products when joining multiple one-to-many relationships (User->Posts->Votes and User->Comments->Votes), I calculated the aggregates separately and merged them efficiently in Python.

**Code:**
```python
post_karma = Post.objects.filter(
    votes__created_at__gte=last_24h
).values('author').annotate(
    score=Count('votes') * 5
)

comment_karma = Comment.objects.filter(
    votes__created_at__gte=last_24h
).values('author').annotate(
    score=Count('votes')
)

# Merge and Sort in Python (O(N) where N is active authors)
```

## The AI Audit
**The Mistake:**
Initial AI suggestions often attempt to implement the Leaderboard using a complex single query on the User model:
```python
User.objects.annotate(
    post_score=Sum(Case(When(posts__votes__created_at__gte=..., then=5))),
    comment_score=Sum(Case(When(comments__votes__created_at__gte=..., then=1)))
)
```
**Why it fails:**
Joining `User -> Posts -> Votes` AND `User -> Comments -> Votes` in a single query creates a **Cartesian Product**, multiplying the rows and producing incorrect sums (e.g., if a user has 2 posts and 2 comments, checks might run 4 times, inflating the score).

**The Fix:**
I split the aggregation into two separate efficient queries (one for posts, one for comments) and merged the results. This avoids the join multiplication issue completely and remains performant for the prototype scale.
