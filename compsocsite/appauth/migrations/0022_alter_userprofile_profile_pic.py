# Generated by Django 4.2.7 on 2024-04-11 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appauth", "0021_userprofile_profile_pic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="profile_pic",
            field=models.ImageField(blank=True, null=True, upload_to="static/img/"),
        ),
    ]
