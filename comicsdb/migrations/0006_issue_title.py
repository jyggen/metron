# Generated by Django 4.0.5 on 2022-06-20 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comicsdb", "0005_genre_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="title",
            field=models.CharField(
                blank=True, max_length=255, verbose_name="Collection Title"
            ),
        ),
    ]
