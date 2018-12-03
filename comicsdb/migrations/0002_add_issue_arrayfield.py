# Generated by Django 2.1.3 on 2018-12-03 14:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comicsdb', '0001_squashed_0004_make_issues_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='tmp_name',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=150, verbose_name='Story Title'), blank=True, null=True, size=None),
        ),
    ]
