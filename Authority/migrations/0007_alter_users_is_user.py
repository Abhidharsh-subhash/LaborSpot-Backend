# Generated by Django 4.2 on 2023-07-11 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authority', '0006_alter_users_is_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='is_user',
            field=models.IntegerField(choices=[(0, 'False'), (1, 'True')], default=0),
        ),
    ]