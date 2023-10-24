import sqlite3
from dataclasses import astuple, fields

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from tqdm import tqdm

from sqlite_to_postgres.models import (
    FilmWork,
    Genre,
    Person,
    GenreFilmWork,
    PersonFilmWork,
)
from sqlite_to_postgres.tests.check_consistency import test_check_consistency

tables_to_extract = {
    "film_work": FilmWork,
    "genre": Genre,
    "person": Person,
    "genre_film_work": GenreFilmWork,
    "person_film_work": PersonFilmWork,
}


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection, tables: dict):
        self.connection = connection
        self.tables = tables
        self.data = {}

    def _extract_table(self, table_name: str, model: type):
        curs = self.connection.cursor()
        curs.execute(f"SELECT * FROM {table_name};")
        data = curs.fetchall()
        column_names = [desc[0] for desc in curs.description]
        result_dicts = [dict(zip(column_names, row)) for row in data]
        objects = [model(**row) for row in result_dicts]
        self.data[table_name] = objects

    def extract(self):
        for table_name, model in tqdm(self.tables.items(), colour="green"):
            self._extract_table(table_name, model)

        return self.data


class PostgresSaver:
    def __init__(self, connection: _connection):
        self.connection = connection

    def _save_table(self, table_name: str, objects: list):
        curs = self.connection.cursor()
        for obj in objects:
            columns = list(obj.model_dump(exclude_none=True).keys())
            column_names = ",".join(columns)
            bind_values = tuple(
                str(value) for value in obj.model_dump(exclude_none=True).values()
            )
            col_count = ", ".join(["%s"] * len(columns))  # '%s, %s

            query = (
                f"INSERT INTO content.{table_name} ({column_names}) VALUES ({col_count})"
                f" ON CONFLICT (id) DO NOTHING"
            )
            curs.execute(query, bind_values)
        self.connection.commit()

    def _prepare_table(self, table_name: str):
        curs = self.connection.cursor()
        curs.execute(f"TRUNCATE TABLE content.{table_name} CASCADE;")
        self.connection.commit()

    def save_all_data(self, data: dict):
        for table_name, objects in tqdm(data.items(), colour="green"):
            self._prepare_table(table_name)
            self._save_table(table_name, objects)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection, tables_to_extract)

    print("Loading data from SQLite to Postgres...")
    data = sqlite_extractor.extract()
    postgres_saver.save_all_data(data)
    print("Data loaded successfully")


if __name__ == "__main__":
    dsl = {
        "dbname": "movies_database",
        "user": "app",
        "password": "123qwe",
        "host": "127.0.0.1",
        "port": 5432,
    }
    with sqlite3.connect("db.sqlite") as sqlite_conn, psycopg2.connect(
        **dsl, cursor_factory=DictCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)

    test_check_consistency()
