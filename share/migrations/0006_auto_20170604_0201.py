# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-04 01:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0005_auto_20170604_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='filelink',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='filelink',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]