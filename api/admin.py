from django.contrib import admin

from api.models import UserMeta, User, Post, Relation, Comment, Like, Follower

admin.site.register(User)
admin.site.register(UserMeta)
admin.site.register(Post)
admin.site.register(Relation)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follower)
