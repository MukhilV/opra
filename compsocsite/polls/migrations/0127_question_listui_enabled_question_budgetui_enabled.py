# Generated by Django 4.2.7 on 2024-02-24 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0126_alter_allocationvoter_id_alter_candscorepair_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='ListUI_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='question',
            name='budgetUI_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
