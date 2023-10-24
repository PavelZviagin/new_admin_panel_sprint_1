import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, validator, field_validator


class CreateUpdateTimeMixin(BaseModel):
    updated_at: datetime | None
    created_at: datetime = field(default_factory=datetime.now)

    @validator("updated_at", "created_at", pre=True, allow_reuse=True)
    def parse_custom_datetime(cls, value):
        if isinstance(value, datetime):
            return value

        parsed_datetime = datetime.strptime(value[:-3], "%Y-%m-%d %H:%M:%S.%f")
        return parsed_datetime


class CreateTimeMixin(BaseModel):
    created_at: datetime = field(default_factory=datetime.now)

    @validator("created_at", pre=True, allow_reuse=True)
    def parse_custom_datetime(cls, value):
        if isinstance(value, datetime):
            return value

        parsed_datetime = datetime.strptime(value[:-3], "%Y-%m-%d %H:%M:%S.%f")
        return parsed_datetime


class FilmWork(CreateUpdateTimeMixin):
    title: str
    description: str | None
    creation_date: datetime | None
    file_path: str | None
    rating: float | None
    type: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class Genre(CreateUpdateTimeMixin):
    name: str
    description: str | None
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class Person(CreateUpdateTimeMixin):
    full_name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class GenreFilmWork(CreateTimeMixin):
    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    id: uuid.UUID = field(default_factory=uuid.uuid4)


class PersonFilmWork(CreateTimeMixin):
    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
