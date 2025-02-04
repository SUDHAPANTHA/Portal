from django.urls import path

from portal_app import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("post-list/", views.PostListView.as_view(), name="post-list"),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path("post-detail/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("about-us/", views.AboutPageView.as_view(), name="about-us"),
    path('post/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add-comment'),
    path('newsletter/', views.NewsletterView.as_view(), name='newsletter'),
    path('search/', views.PostSearchView.as_view(), name='post-search'),
]