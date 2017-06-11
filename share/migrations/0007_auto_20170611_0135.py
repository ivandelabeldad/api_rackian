# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-11 00:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('share', '0006_auto_20170604_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filelink',
            name='file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='storage.File'),
        ),
        migrations.AlterField(
            model_name='folderlink',
            name='folder',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='storage.Folder'),
        ),
    ]