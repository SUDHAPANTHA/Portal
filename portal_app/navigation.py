from portal_app.models import Category, Post, Tag


def nav(request):
    tags = Tag.objects.all()[:10]
    categories = Category.objects.all()[:3]
    trending_posts = Post.objects.filter(
        published_at__isnull = False, status="active"
    ).order_by("-views_count")[:3]
    side_categories = Category.objects.all()[:6]
    return { 
        "tags": tags,
        "categories": categories,
        "trending_posts": trending_posts,
        "side_categories": side_categories,
    }