# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-01 04:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0093_uservoterecord_swit'),
    ]

    operations = [
        migrations.AddField(
            model_name='uservoterecord',
            name='col',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='uservoterecord',
            name='record',
            field=models.CharField(default='', max_length=10000),
        ),
    ]
