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
    """
    Construye la cadena de conexión a PostgreSQL desde variables de entorno.
    
    Variables esperadas:
    - DB_HOST (default: localhost)
    - DB_PORT (default: 5432)
    - DB_NAME
    - DB_USER
    - DB_PASSWORD
    """
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
    """
    Context manager para obtener una conexión a la BD.
    Se cierra automáticamente al salir del contexto.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
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
    """
    Ejecuta una consulta SELECT y retorna los resultados como lista de diccionarios.
    
    Args:
        query: Query SQL
        params: Parámetros para la query (tupla)
    
    Returns:
        Lista de diccionarios con los resultados
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def execute_update(query: str, params: Optional[tuple] = None) -> int:
    """
    Ejecuta una consulta UPDATE/INSERT/DELETE y retorna el número de filas afectadas.
    
    Args:
        query: Query SQL
        params: Parámetros para la query (tupla)
    
    Returns:
        Número de filas afectadas
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount

