import yaml
from typing import Union, Dict

import psycopg2

from settings import secret_path


class PostgresClient:
    def __init__(self):
        with open(secret_path, "r", encoding="utf-8") as f:
            __secret = yaml.safe_load(f)
        __host = __secret["postgresql"]["host"]
        __port = __secret["postgresql"]["port"]
        __database = __secret["postgresql"]["database"]
        __username = __secret["postgresql"]["username"]
        __password = __secret["postgresql"]["password"]

        if not hasattr(self, "conn") or self.conn is None:
            self.conn = psycopg2.connect(
                host=__host, port=__port, dbname=__database, user=__username, password=__password
            )

    def __del__(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()
            self.conn = None

    def insert(self, table: str, data: Dict):
        if not isinstance(data, Dict):
            raise Exception("The variable 'data' must be a dictionary")

        columns = ", ".join(data.keys())
        values = ", ".join(f"%s" for _ in data.values())
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        # Execute the SQL command with the values
        with self.conn.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
