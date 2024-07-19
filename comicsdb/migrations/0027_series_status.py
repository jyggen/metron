# Generated by Django 5.0.7 on 2024-07-14 13:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comicsdb", "0026_announcement"),
    ]

    operations = [
        migrations.AddField(
            model_name="series",
            name="status",
            field=models.IntegerField(
                choices=[(1, "Cancelled"), (2, "Completed"), (3, "Hiatus"), (4, "Ongoing")],
                default=4,
            ),
        ),
    ]
