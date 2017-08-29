from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from infos.models import District, Subject, ClassLevel


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, related_name='auth_posts')
    created_at = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(Subject, null=True, blank=True)
    class_level = models.ForeignKey(ClassLevel, null=True, blank=True)
    salary_hour = models.IntegerField(validators=[MinValueValidator(0)], default=100000)
    times_week = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], default=1)
    district = models.ForeignKey(District, related_name='district_posts', null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='like_posts')
    is_approved = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def is_tutor(self):
        return self.author.is_tutor

    def get_absolute_url(self):
        return reverse('posts:detail_post', kwargs={'pk': self.id})

    def get_liked_users(self):
        return self.likes.all()

    class Meta:
        ordering = ('created_at',)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='post_comments')
    author = models.ForeignKey(User, related_name='auth_comments')
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
