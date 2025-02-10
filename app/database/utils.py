from typing import Dict, List

from database.client import PostgresClient


def get_chat_history(username: str, client: PostgresClient) -> List[Dict]:
    sql = f"""
    SELECT *
      FROM chat
     WHERE username='{username}'
     ORDER BY create_datetime
    """

    with client.conn.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    if rows:
        return [
            {
                "session_id": row[1],
                "username": row[2],
                "ip": row[3],
                "role": row[4],
                "content": row[5],
                "create_datetime": row[6],
            }
            for row in rows
        ]
    else:
        return []


def delete_chat_hitory(username: str, client: PostgresClient):
    sql = f"""
    DELETE FROM chat
     WHERE username='{username}'
    """

    with client.conn.cursor() as cursor:
        cursor.execute(sql)
        client.conn.commit()
