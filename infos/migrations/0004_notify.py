# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-12 09:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('infos', '0003_auto_20170804_0844'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notify',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('noti_type', models.CharField(blank=True, choices=[('like', 'like'), ('comment', 'comment'), ('rating', 'rating')], max_length=10, null=True)),
                ('from_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('to_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]