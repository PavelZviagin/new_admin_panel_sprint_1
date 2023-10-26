import csv
import os
import sqlite3
from dotenv import load_dotenv
from loguru import logger as logging
import tempfile

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
    def __init__(self, connection: sqlite3.Connection, tables: dict, postgres_saver: 'PostgresSaver'):
        self.connection = connection
        self.tables = tables
        self.postgres_saver = postgres_saver

    def _extract_table(self, table_name: str):
        self.postgres_saver.prepare_table(table_name)
        curs = self.connection.cursor()
        curs.execute(f"SELECT * FROM {table_name};")
        column_names = [desc[0] for desc in curs.description]
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            csv_writer = csv.writer(temp_file, delimiter='\t', escapechar='\\', quoting=csv.QUOTE_NONE)
            while True:
                data = curs.fetchmany(1000)

                if not data:
                    break

                for row in data:
                    csv_writer.writerow(row)

        self.postgres_saver.save_from_file(temp_file.name, table_name, column_names)

    def extract(self):
        for table_name, model in tqdm(self.tables.items(), colour="green"):
            self._extract_table(table_name)


class PostgresSaver:
    def __init__(self, connection: _connection):
        self.connection = connection

    def save_from_file(self, file, table, column_names):
        curs = self.connection.cursor()
        try:
            with open(file, 'r') as f:
                curs.copy_from(f, table, sep='\t', null='', columns=column_names)
        finally:
            os.remove(file)
        self.connection.commit()

    def prepare_table(self, table_name: str):
        curs = self.connection.cursor()
        curs.execute(f"TRUNCATE TABLE content.{table_name} CASCADE;")
        self.connection.commit()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(connection, tables_to_extract, postgres_saver)

    logging.info("Loading data from SQLite to Postgres...")
    sqlite_extractor.extract()
    logging.info("Data loaded successfully")


if __name__ == "__main__":
    load_dotenv()

    dsl = {
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
        "host": os.environ.get("DB_HOST"),
        "port": os.environ.get("DB_PORT"),
        'options': '-c search_path=public,content'
    }

    sqlite_conn = sqlite3.connect("db.sqlite")
    pg_conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)

    try:
        with sqlite_conn, pg_conn:
            load_from_sqlite(sqlite_conn, pg_conn)
    finally:
        sqlite_conn.close()
        pg_conn.close()

    test_check_consistency()
