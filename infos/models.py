from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class School(models.Model):
    name = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class ClassLevel(models.Model):
    class_level = models.IntegerField(validators=[MaxValueValidator(12), MinValueValidator(1)], null=True, blank=True)

    def __str__(self):
        return str(self.class_level)


class Rating(models.Model):
    from_user = models.ForeignKey('accounts.User', null=True, related_name="+")
    to_user = models.ForeignKey('accounts.User', null=True, related_name="+")
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(0)], null=True, blank=True)


class Notify(models.Model):
    LIKE = '1'
    COMMENT = '2'
    RATING = '3'
    NOTI_CHOICES = (
        (LIKE, 'like'),
        (COMMENT, 'comment'),
        (RATING, 'rating')
    )

    from_user = models.ForeignKey('accounts.User', null=True, related_name="+")
    to_user = models.ForeignKey('accounts.User', null=True, related_name="+")
    noti_type = models.CharField(choices=NOTI_CHOICES, max_length=10, null=True, blank=True)
    noti_post = models.ForeignKey('posts.Post', null=True, related_name="+")
    rating = models.IntegerField(default=-1)
    seen = models.BooleanField(default=False)
    noti_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} {} {}".format(self.from_user.username, self.noti_type, self.to_user.username)

    def get_noti_str(self):
        if self.noti_type == self.LIKE:
            return "{user} likes your post: {post_name}.".format(
                user=self.from_user.username,
                post_name=self.noti_post.title
            )
        elif self.noti_type == self.COMMENT:
            return "{user} also commented to post: {post_name}.".format(
                user=self.from_user.username,
                post_name=self.noti_post.title
            )
        else:
            return "{user} rate you {rating} stars.".format(
                user=self.from_user.username,
                rating=self.rating
            )
