# Generated by Django 4.2 on 2023-07-19 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='phone_number',
            field=models.BigIntegerField(),
        ),
    ]