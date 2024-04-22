# Generated by Django 4.2.7 on 2024-04-11 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appauth", "0020_alter_userprofile_salt"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="profile_pic",
            field=models.ImageField(
                blank=True, null=True, upload_to="static/img/items/"
            ),
        ),
    ]
