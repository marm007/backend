from django.contrib import admin
from django.conf import settings

from api.models import Comment, Follower, Like, Post, PostMeta, Relation, RelationMeta, User, UserMeta


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


class UserAdminModel(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

class CommentInline(admin.TabularInline):
    model = Comment


class MetaInline(admin.TabularInline):
    model = UserMeta


class RelationInline(admin.TabularInline):
    model = Relation


class PostInline(admin.TabularInline):
    model = Post


class PostMetaInline(admin.TabularInline):
    model = PostMeta


class RelationMetaInline(admin.TabularInline):
    model = RelationMeta

class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline, PostMetaInline]
    list_display = ('__str__', 'user', 'image', 'description',
                    'likes', 'created', 'updated')
    list_filter = ('likes', 'created', 'user')
    date_hierarchy = 'created'
    ordering = ('likes', 'created')


class UserAdmin(UserAdminModel):
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

class CommentAdmin(CommentAdmin):
    list_display = ('__str__', 'body', 'active')

class LikeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'post', 'created')

class FollowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'user_being_followed',
                    'started_following')

class RelationAdmin(admin.ModelAdmin):
    inlines = [RelationMetaInline, ]
    list_display = ('__str__', 'user')

class UserMetaAdmin(admin.ModelAdmin):
    list_display = ('__str__', )

class PostMetaAdmin(admin.ModelAdmin):
    list_display = ('__str__', )

class RelationMetaAdmin(admin.ModelAdmin):
    list_display = ('__str__', )

from django.contrib.admin import AdminSite
class MyAdminSite(AdminSite):
    login_template = "api/templates/admin/login.html"
    site_title = "PhotoApp Admin Portal"
    site_header = "PhotoApp Admin"
    index_title = "Welcome to PhotoApp Admin Portal"
    site_url = settings.FRONT_URL


site = MyAdminSite()

site.register(Post, PostAdmin)
site.register(User, UserAdmin)
site.register(Comment, CommentAdmin)
site.register(Like, LikeAdmin)
site.register(Follower, FollowerAdmin)
site.register(Relation, RelationAdmin)
site.register(UserMeta, UserMetaAdmin)
site.register(PostMeta, PostMetaAdmin)
site.register(RelationMeta, RelationMetaAdmin)
