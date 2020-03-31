from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class User(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return "{}".format(self.email)


class UserMeta(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='meta')
    avatar = CloudinaryField('avatars')

    is_private = models.BooleanField(default=False)
    reset_password_token = models.SlugField(max_length=250, blank=True)
    reset_password_expires = models.DateTimeField(auto_now_add=True)


class Album(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='album')
    photos = models.ManyToManyField('Post', blank=True)


class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed')
    user_being_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    started_following = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'user_being_followed',)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    image = CloudinaryField('posts')
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    author_name = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.user


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post',)


class Relation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relations')
    image = CloudinaryField('relations')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
