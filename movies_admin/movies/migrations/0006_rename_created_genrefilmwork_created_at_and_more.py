# Generated by Django 4.2.5 on 2023-10-24 09:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0005_remove_filmwork_certificate"),
    ]

    operations = [
        migrations.RenameField(
            model_name="genrefilmwork",
            old_name="created",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="personfilmwork",
            old_name="created",
            new_name="created_at",
        ),
    ]
