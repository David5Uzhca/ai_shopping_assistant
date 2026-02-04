"""
Módulo para manejar la conexión a PostgreSQL.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv(".env")

def get_db_connection_string() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    if not all([dbname, user, password]):
        raise ValueError(
            "Faltan variables de entorno para la BD: DB_NAME, DB_USER, DB_PASSWORD"
        )
    
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn_string = get_db_connection_string()
        conn = psycopg2.connect(conn_string)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def execute_update(query: str, params: Optional[tuple] = None) -> int:
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

