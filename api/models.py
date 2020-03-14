from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class User(AbstractUser):
    username = models.CharField(max_length=25)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return "{}".format(self.email)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)


class Album(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='album')
    photos = models.ManyToManyField('Photo')


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.FileField(upload_to='images')
    description = models.TextField()
    likes = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='liked')

    class Meta:
        unique_together = ('user', 'photo',)


