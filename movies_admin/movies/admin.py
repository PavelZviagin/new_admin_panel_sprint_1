from django.contrib import admin
from .models import Genre, FilmWork, GenreFilmwork, PersonFilmwork, Person


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")

    search_fields = ("name", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created_at", "updated_at")

    search_fields = ("full_name", "id")


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )

    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
        "created_at",
        "updated_at",
    )

    list_filter = ("type",)

    search_fields = ("title", "description", "id")
