# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-29 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appauth', '0013_auto_20171229_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='time_creation',
            field=models.DateTimeField(),
        ),
    ]