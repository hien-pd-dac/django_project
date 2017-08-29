from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.urls import reverse

from infos import models as infos_models
from infos.models import Notify

GENDER_CHOICES = (
    ('M', 'Male'), ('F', 'Female')
)


class User(AbstractUser):
    first_name = models.CharField(max_length=20, default='NoName')
    telephone = models.CharField(max_length=11, null=True, blank=True)
    dateofbirth = models.DateField(max_length=8, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, null=True, blank=True)
    school = models.CharField(max_length=50, null=True, blank=True)
    classname = models.CharField(max_length=10, null=True, blank=True)
    favorite_subject = models.ForeignKey(infos_models.Subject, related_name='favor_sub_users', null=True, blank=True)
    is_tutor = models.BooleanField(default=False)
    district = models.ForeignKey(infos_models.District, related_name='district_users', null=True, blank=True)
    intro_yourself = models.TextField(max_length=256, null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pic', default='profile_pic/profile.jpg')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.pk})

    def count_raters(self):
        return infos_models.Rating.objects.filter(to_user=self).count()

    def get_rating_other(self, user_id):
        user = get_object_or_404(User, id=user_id)
        try:
            rate = infos_models.Rating.objects.get(from_user=self, to_user=user)
            return rate.rating
        except infos_models.Rating.DoesNotExist:
            return 0

    def calculate_avg_rating(self):
        rating_qs = infos_models.Rating.objects.filter(to_user=self)
        num_rating = rating_qs.count()
        rating_avg = rating_qs.aggregate(Avg('rating'))['rating__avg']
        if rating_avg is None:
            return 0

        if num_rating < 3:
            return (num_rating * rating_avg) / 3

        return rating_avg

    def str_avg_rating(self):
        avg = self.calculate_avg_rating()
        return '{:03.2f}'.format(avg)

    def get_num_unread_noties(self):
        return Notify.objects.filter(to_user=self, seen=False).count()
