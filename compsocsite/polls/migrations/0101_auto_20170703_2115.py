# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-04 01:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0100_folder'),
    ]

    operations = [
        migrations.RenameField(
            model_name='folder',
            old_name='title',
            new_name='titl',
        ),
    ]
