from django.contrib import admin

from portal_app.models import Category, Comment, Contact, Newsletter, Post, Tag, UserProfile

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Newsletter)