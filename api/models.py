import uuid

from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from model_utils.models import TimeFramedModel
from django.db.models import Q


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    def __str__(self):
        return "{}".format(self.email)


class UserMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='meta')
    avatar = CloudinaryField('avatar', blank=True)

    is_private = models.BooleanField(default=True)
    reset_password_token = models.SlugField(max_length=250, blank=True)
    reset_password_expires = models.DateTimeField(auto_now_add=True)

    activation_token = models.SlugField(max_length=250, blank=True)
    activation_token_expires = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.user.email)


class Follower(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followed')
    user_being_followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    started_following = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'user_being_followed',)

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')

    image = CloudinaryField('image')
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def output_comments(self):
        return Comment.objects.all().order_by('created').filter(Q(post=self) & Q(active=True))[:2]

    def image_metadata(self):
        try:
            meta = self.image.metadata
        except AttributeError:
            meta = ''
        return meta


class PostImageMeta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="meta")
    width = models.IntegerField()
    height = models.IntegerField()
    url = models.TextField()
    public_id = models.CharField(max_length=150, blank=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    author_name = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='liked')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post',)


class Relation(TimeFramedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='relations')
    image = CloudinaryField('image')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
