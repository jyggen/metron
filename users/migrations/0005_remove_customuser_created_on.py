# Generated by Django 3.2.3 on 2021-05-13 19:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_add_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='created_on',
        ),
    ]
