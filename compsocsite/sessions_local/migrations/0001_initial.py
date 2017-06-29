# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-29 13:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('link', models.TextField(default='')),
                ('pub_date', models.DateTimeField(verbose_name='date published')),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sessions_created', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='sessions_participated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
