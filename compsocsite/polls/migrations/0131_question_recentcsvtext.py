# Generated by Django 4.2.7 on 2024-05-26 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0130_question_alloc_algorithms"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="recentCSVText",
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
