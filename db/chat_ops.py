from typing import List, Dict, Any
from db.connection import execute_query, execute_update

def save_chat_message(user_id: str, role: str, content: str, session_id: str = None):
    """    Guarda un mensaje en el historial.    """
    query = """
        INSERT INTO chat_history (user_id, role, content, session_id)
        VALUES (%s, %s, %s, %s)
    """
    execute_update(query, (user_id, role, content, session_id))

def get_recent_chat_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    query = """
        SELECT role, content 
        FROM chat_history 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """
    rows = execute_query(query, (user_id, limit))
    
    # Invertimos para retornar en orden cronológico (viejo -> nuevo)
    return rows[::-1]

def clear_chat_history(user_id: str):
    query = "DELETE FROM chat_history WHERE user_id = %s"
    execute_update(query, (user_id,))
