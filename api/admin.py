from django.contrib import admin

from api.models import UserMeta, User, Post, Relation, Comment, Like, Follower


class CommentInline(admin.TabularInline):
    model = Comment


admin.site.register(User)
admin.site.register(UserMeta)
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = ('user', 'image', 'likes', 'created', 'updated')


admin.site.register(Relation)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follower)
