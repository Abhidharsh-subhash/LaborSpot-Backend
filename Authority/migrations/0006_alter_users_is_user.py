# Generated by Django 3.2.19 on 2023-07-10 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authority', '0005_alter_users_is_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='is_user',
            field=models.IntegerField(choices=[(1, 'True'), (0, 'False')], default=0),
        ),
    ]
