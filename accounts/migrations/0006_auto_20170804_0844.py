# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 01:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_delete_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='raters',
        ),
        migrations.RemoveField(
            model_name='user',
            name='rating',
        ),
    ]