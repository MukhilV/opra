# Generated by Django 4.2.7 on 2023-12-08 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessions_local', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
