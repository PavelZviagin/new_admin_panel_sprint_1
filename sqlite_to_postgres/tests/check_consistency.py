import sqlite3

import psycopg2
from psycopg2.extras import DictCursor


def compare_data_between_databases(sqlite_conn, postgres_conn):
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()

    # Список таблиц для проверки
    tables_to_check = [
        "genre",
        "film_work",
        "person",
        "genre_film_work",
        "person_film_work",
    ]

    for table in tables_to_check:
        # Проверка количества записей в каждой таблице
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        postgres_cursor.execute(f"SELECT COUNT(*) FROM content.{table}")

        sqlite_count = sqlite_cursor.fetchone()[0]
        postgres_count = postgres_cursor.fetchone()[0]

        assert (
            sqlite_count == postgres_count
        ), f"Количество записей в таблице {table} не совпадает (SQLite: {sqlite_count}, PostgreSQL: {postgres_count})"

        # Проверка содержимого записей внутри каждой таблицы
        sqlite_cursor.execute(f"SELECT id FROM {table}")
        sqlite_data = sorted(sqlite_cursor.fetchall())

        postgres_cursor.execute(f"SELECT id FROM content.{table}")
        postgres_data = sorted(postgres_cursor.fetchall())

        for i, k in zip(sqlite_data, postgres_data):
            assert (
                i[0] == k[0]
            ), f"Содержимое записей в таблице {table} не совпадает (SQLite: {i}, PostgreSQL: {k})"

    sqlite_cursor.close()
    postgres_cursor.close()


def test_check_consistency():
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
        compare_data_between_databases(sqlite_conn, pg_conn)
