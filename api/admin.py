from django.contrib import admin

from api.models import Comment, Follower, Like, Post, Relation, User, UserMeta
from django.contrib.auth.models import Group


admin.site.site_header = "PhotoApp Admin"
admin.site.site_title = "PhotoApp Admin Portal"
admin.site.index_title = "Welcome to PhotoApp Admin Portal "


class CommentAdmin(admin.ModelAdmin):
    actions = ['make_inactive', 'make_active']

    def make_inactive(self, request, queryset):
        queryset.update(active=False)

    make_inactive.short_description = "Mark selected stories as unpublished"
    make_inactive.allowed_permissions = ('change',)

    def make_active(self, request, queryset):
        queryset.update(active=True)

    make_active.short_description = "Mark selected stories as published"
    make_active.allowed_permissions = ('change',)


class UserAdmin(admin.ModelAdmin):
   def has_delete_permission(self, request, obj=None):
        return False

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
class UserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = User.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()

    inlines = [MetaInline, PostInline, CommentInline, RelationInline]
    list_display = ('email', 'username', 'last_name', 'first_name', 'is_staff')


@admin.register(Comment)
class CommentAdmin(CommentAdmin):
    list_display = ('__str__', 'body', 'active')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'post', 'created')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'user_being_followed' , 'started_following')


@admin.register(Relation)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')


@admin.register(UserMeta)
class UserMetaAdmin(admin.ModelAdmin):
    list_display = ('__str__', )
