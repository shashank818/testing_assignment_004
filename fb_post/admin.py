from django.contrib import admin
from fb_post.models import Post, Comment, Reaction, User

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(User)
