from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from datetime import timedelta
from django.utils import timezone
from django.views.generic.edit import FormView
from portal_app.forms import ContactForm
from portal_app.models import Category, Comment, Post, Tag
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView
from django.contrib import messages
from .models import Comment, Post
from django.http import JsonResponse
from portal_app.forms import NewsletterForm
from django.core.paginator import PageNotAnInteger, Paginator
from django.db.models import Q


class AboutPageView(ListView):
    model = Post
    template_name = "aznews/about.html"
    context_object_name = "posts"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    

        context["trending_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-views_count")[:3]

class HomePageView(ListView):
    model = Post
    template_name = "aznews/home.html"
    context_object_name = "posts"
    # queryset = Post.objects.filter(
    #     published_at_isnull=False, status="active"
    # ).order_by("-publised_at")[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    

        context["trending_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-views_count")[:3]

        context["featured_post"] = (
            Post.objects.filter(published_at__isnull=False, status="active")
            .order_by("-published_at", "-views_count")
            .first()
        )
        context["featured_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at", "-views_count")[1:4]

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
    published_at__isnull=False, status="active", published_at__gte=timezone.now() - timedelta(days=14)
).order_by("-published_at", "-views_count")[:7]


        context["recent_posts"] = Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")[:7]

        context['tags'] = Tag.objects.all()[:10]
        context['categories'] = Category.objects.all()[:3]

        return context
    

class ContactView(FormView):
    template_name = 'aznews/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')  

    def form_valid(self, form):
        messages.success(self.request, "Your message has been sent successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in your submission. Please correct it.")
        return super().form_invalid(form)

class PostListView(ListView):
    model = Post
    template_name = "aznews/list/list.html"
    context_object_name = "posts"
    paginate_by = 1

    def get_queryset(self):
        return Post.objects.filter(
            published_at__isnull=False, status="active"
        ).order_by("-published_at")
class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/detail/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(published_at__isnull=False, status="active")
        return query
def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        # 7 => 1, 2, 3, 4, 5, 6 => 6, 5, 4, 3, 2, 1
        context["previous_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__lt=obj.id
            )
            .order_by("-id")
            .first()
        )

        # 8, 9, 10 ....
        context["next_post"] = (
            Post.objects.filter(
                published_at__isnull=False, status="active", id__gt=obj.id
            )
            .order_by("id")
            .first()
        )

        return context
# def post(self, request, *args, **kwargs):
    # """Handle comment form submission."""
    # obj = self.get_object()  
    # print(request.POST) 

    # comment_text = request.POST.get("comment")
    # name = request.POST.get("name")
    # email = request.POST.get("email")

    # if comment_text and name and email:
    #     Comment.objects.create(
    #         post=obj,
    #         comment=comment_text,
    #         name=name,
    #         email=email
    #     )
    #     messages.success(request, "Your comment was successfully submitted!")
    #     return redirect("post-detail", pk=obj.pk)

    # messages.error(request, "Please fill out all required fields.")
    # return redirect("post-detail", pk=obj.pk)

    # """Handle comment form submission."""
    # obj = self.get_object()  
    # comment_text = request.POST.get("comment")
    # name = request.POST.get("name")
    # email = request.POST.get("email")

    # if comment_text and name and email:
    #     Comment.objects.create(
    #         post=obj,
    #         comment=comment_text,
    #         name=name,
    #         email=email
    #     )
    #     messages.success(request, "Your comment was successfully submitted!")
    #     return redirect("post-detail", pk=obj.pk)

    # # Add error message to context if validation fails
    # messages.error(request, "Please fill out all required fields.")
    # return redirect("post-detail", pk=obj.pk)


class CommentCreateView(CreateView):
    model = Comment
    fields = ['comment', 'name', 'email']
    template_name = "comment_form.html"  # Ensure this template exists

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.save()
        messages.success(self.request, "Your comment was successfully submitted!")
        return redirect('post-detail', pk=post.pk)

    def form_invalid(self, form):
        messages.error(self.request, "Please fill out all required fields.")
        return redirect('post-detail', pk=self.kwargs['pk'])



class NewsletterView(View):
    def post(self, request):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfully subscribed to the newsletter.",
                    },
                    status=201,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Cannot subscribe to the newsletter.",
                    },
                    status=400,
                )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process. Must be an AJAX XMLHttpRequest",
                },
                status=400,
            )




class PostSearchView(View):
    template_name = "aznews/list/list.html"

    def get(self, request, *args, **kwargs):
        query = request.GET["query"]  # query=plus search => title=plus or content=plus
        post_list = Post.objects.filter(
            (Q(title__icontains=query) | Q(content__icontains=query))
            & Q(status="active")
            & Q(published_at__isnull=False)
        ).order_by("-published_at")

        # pagination start
        page = request.GET.get("page", 1)  # 2
        paginate_by = 3
        paginator = Paginator(post_list, paginate_by)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        # pagination end

        return render(
            request,
            self.template_name,
            {"page_obj": posts, "query": query},
        )
