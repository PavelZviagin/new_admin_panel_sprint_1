# Generated by Django 4.2.5 on 2023-10-24 07:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0003_rename_created_filmwork_created_at_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="filmwork",
            old_name="modified_at",
            new_name="updated_at",
        ),
        migrations.RenameField(
            model_name="genre",
            old_name="modified_at",
            new_name="updated_at",
        ),
        migrations.RenameField(
            model_name="person",
            old_name="modified_at",
            new_name="updated_at",
        ),
    ]