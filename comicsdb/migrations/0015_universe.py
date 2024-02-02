# Generated by Django 5.0.1 on 2024-01-20 15:47

import django.db.models.deletion
import django.db.models.functions.datetime
import sorl.thumbnail.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comicsdb", "0014_series_collection"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Universe",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("desc", models.TextField(blank=True, verbose_name="Description")),
                (
                    "cv_id",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Comic Vine ID"
                    ),
                ),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "created_on",
                    models.DateTimeField(db_default=django.db.models.functions.datetime.Now()),
                ),
                (
                    "image",
                    sorl.thumbnail.fields.ImageField(blank=True, upload_to="universe/%Y/%m/%d/"),
                ),
                ("designation", models.CharField(blank=True, max_length=255)),
                (
                    "edited_by",
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "publisher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="comicsdb.publisher"
                    ),
                ),
            ],
            options={
                "db_table_comment": "Publisher Universes",
                "ordering": ["name", "designation"],
                "indexes": [models.Index(fields=["name"], name="universe_name_idx")],
            },
        ),
    ]
