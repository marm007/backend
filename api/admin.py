from django.contrib import admin

from api.models import UserMeta, User, Post, Relation, Comment, Like, Follower
from django.contrib.auth.models import Group

admin.site.unregister(Group)


class CommentInline(admin.TabularInline):
    model = Comment


class MetaInline(admin.TabularInline):
    model = UserMeta


class RelationInline(admin.TabularInline):
    model = Relation


class PostInline(admin.TabularInline):
    model = Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = ('__str__', 'user', 'description', 'likes', 'created', 'updated')
    list_filter = ('likes', 'created', 'user')
    date_hierarchy = 'created'
    ordering = ('likes', 'created')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [MetaInline, PostInline, CommentInline, RelationInline]
    list_display = ('email', 'username', 'last_name', 'first_name', 'is_staff')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'body')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'post', 'created')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'user_being_followed' , 'started_following')


@admin.register(Relation)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')


admin.site.register(UserMeta)
