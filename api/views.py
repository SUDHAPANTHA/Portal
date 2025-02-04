from django.contrib.auth.models import Group, User
from django.db import models
from django.utils import timezone
from rest_framework import exceptions, permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    ContactSerializer,
    GroupSerializer,
    NewsletterSerializer,
    PostPublishSerializer,
    PostSerializer,
    TagSerializer,
    UserSerializer,
)
from portal_app.models import Category, Comment, Contact, Newsletter, Post, Tag


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Tags to be viewed or edited.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return super().get_permissions()


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Categories to be viewed or edited.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]

        return super().get_permissions()


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Posts to be viewed or edited.
    """

    queryset = Post.objects.all().order_by("-published_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [SearchFilter]
    search_fields = ["title", "content"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.filter(status="active", published_at__isnull=False)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [permissions.AllowAny()]
        return super().get_permissions()

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     if self.action in ["list", "retrieve"]:
    #         queryset = queryset.filter(status="active", published_at__isnull=False)

    #         # search start:
    #         from django.db.models import Q
    #         search_term = self.request.query_params.get("search", None)
    #         if search_term:
    #             # Search by title and content (case-insensitive)
    #             queryset = queryset.filter(
    #                 Q(title__icontains=search_term) | Q(content__icontains=search_term)
    #             )
    #         # search end
    #     return queryset

    def retrieve(self, request, *args, **kwargs):
        # Get the object instance
        instance = self.get_object()

        # Increment the views_count
        instance.views_count = models.F("views_count") + 1
        instance.save(update_fields=["views_count"])  # Use update_fields for efficiency

        # Refresh the instance from the database to ensure the updated value is reflected
        instance.refresh_from_db()

        # Serialize and return the data
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     instance.views_count += 1  # Increment the views_count
    #     instance.save(update_fields=["views_count"])  # Save only the updated field
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


class DraftListViewSet(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(published_at__isnull=True)
        return queryset

class PostListByCategoryViewSet(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["category_id"],
        )
        return queryset


class PostListByTagViewSet(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status="active",
            published_at__isnull=False,
            tag=self.kwargs["tag_id"],
        )
        return queryset


class PostPublishViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostPublishSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data

            # publish the post
            post = Post.objects.get(pk=data["id"])
            post.published_at = timezone.now()
            post.save()

            serialized_data = PostSerializer(post).data
            return Response(serialized_data, status=status.HTTP_200_OK)


class NewsletterViewSet(viewsets.ModelViewSet):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        raise exceptions.MethodNotAllowed(request.method)


class CommentViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, post_id, *args, **kwargs):
        comments = Comment.objects.filter(post=post_id).order_by("-created_at")
        serialized_data = CommentSerializer(comments, many=True).data
        return Response(serialized_data, status=status.HTTP_200_OK)

    def post(self, request, post_id, *args, **kwargs):
        request.data.update({"post": post_id})
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.db.models import Case, F, Q, Sum, When

published_and_active = Q(status="published", published_at__isnull=False)


class TopCategoriesListViewSet(ListAPIView):
    """
    List all Top categories that has maximum views_count posts
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        top_categories = (
            Post.objects.filter(published_and_active)
            .values("category__pk", "category__name")
            .annotate(
                pk=F("category__pk"),
                name=F("category__name"),
                max_views=Sum("views_count"),
            )
            .order_by("-views_count")
            .values("pk", "name", "max_views")
        )
        # [2,6,5,6]
        category_ids = [top_category["pk"] for top_category in top_categories]
        order_by_max_views = Case(
            *[
                When(id=category["pk"], then=category["max_views"])
                for category in top_categories
            ]
        )
        top_categories = Category.objects.filter(pk__in=category_ids).order_by(
            -order_by_max_views
        )
        return top_categories
