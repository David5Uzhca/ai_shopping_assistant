
"""
Módulo para operaciones de usuarios (User Repository).
Maneja creación, autenticación y búsquedas en la BD.
"""
from typing import Optional, Dict, Any
from db.connection import execute_query, execute_update
from passlib.context import CryptContext

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # bcrypt tiene un límite de 72 bytes
    if len(password.encode('utf-8')) > 72:
        raise ValueError("La contraseña es demasiado larga (máximo 72 caracteres).")
    return pwd_context.hash(password)

def create_user(user_data: Dict[str, Any]) -> str:
    """
    Crea un nuevo usuario en la base de datos.
    Retorna el ID del usuario creado o lanza una excepción si falla.
    """
    query = """
    INSERT INTO users (
        first_name, last_name, gender, age, 
        email, phone, password_hash
    ) VALUES (
        %s, %s, %s, %s, 
        %s, %s, %s
    ) RETURNING user_id;
    """
    
    # Hashear contraseña antes de guardar
    hashed_pwd = get_password_hash(user_data["password"])
    
    params = (
        user_data["first_name"],
        user_data["last_name"],
        user_data["gender"],
        user_data["age"],
        user_data["email"],
        user_data["phone"],
        hashed_pwd
    )
    
    try:
        results = execute_query(query, params)
        if results:
            return str(results[0]["user_id"])
        raise Exception("No se pudo obtener el ID del usuario creado.")
    except Exception as e:
        # Manejo básico de errores de duplicados (Postgres lanza error de integridad)
        if "unique constraint" in str(e).lower():
            if "email" in str(e).lower():
                raise ValueError("El correo electrónico ya está registrado.")
            if "phone" in str(e).lower():
                raise ValueError("El número de celular ya está registrado.")
        raise e

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifica credenciales. Retorna los datos del usuario si es válido, o None.
    """
    query = """
    SELECT user_id, first_name, last_name, email, password_hash, age, gender 
    FROM users 
    WHERE email = %s AND is_active = true
    """
    
    results = execute_query(query, (email,))
    
    if not results:
        return None
        
    user = results[0]
    
    if verify_password(password, user["password_hash"]):
        # No devolver el hash
        user.pop("password_hash")
        return user
        
    return None

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT user_id, first_name, last_name, email, age, gender FROM users WHERE user_id = %s"
    results = execute_query(query, (user_id,))
    return results[0] if results else None
