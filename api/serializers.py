from django.contrib.auth.models import Group, User
from rest_framework import serializers
from portal_app.models import Category, Comment, Contact, Newsletter, Post, Tag


# ORM => Object Relationship Mapping
# Post.objects.all() => SELECT * FROM posts; => Queryset[<Post 1>, <Post 2>, <Post 3>]
# Post.objects.create(....)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "groups",
            "first_name",
            "is_active",
            "is_superuser",
        ]

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'published_at']
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "featured_image",
            "status",
            "tag",
            "category",
            # read only
            "author",
            "views_count",
            "published_at",
        ]
        extra_kwargs = {
            "author": {"read_only": True},
            "views_count": {"read_only": True},
            "published_at": {"read_only": True},
        }

    def validate(self, data):
        data["author"] = self.context["request"].user
        return data


class PostPublishSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
