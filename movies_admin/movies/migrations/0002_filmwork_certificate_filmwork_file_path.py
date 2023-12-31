# Generated by Django 4.2.5 on 2023-10-23 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="filmwork",
            name="certificate",
            field=models.CharField(
                blank=True, max_length=512, verbose_name="certificate"
            ),
        ),
        migrations.AddField(
            model_name="filmwork",
            name="file_path",
            field=models.FileField(
                blank=True, null=True, upload_to="movies/", verbose_name="file"
            ),
        ),
    ]
