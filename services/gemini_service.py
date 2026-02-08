import os
import uuid
from typing import Dict, Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import tools
from tools.basic_tools import get_supermarket_hour, get_product_location, get_supermarket_details
from tools.product_tools import search_products, compare_products
from tools.cart_tools import add_product_to_cart_tool, view_cart_tool, checkout_cart_tool

# Import DB
from db.user_ops import get_user_by_id
from db.chat_ops import get_recent_chat_history

load_dotenv(".env")

# --- Gemini Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
MODEL_ID = "gemini-3-flash-preview"
MODEL_FALLBACK = "gemini-2.0-flash-exp"

# Session Storage
chat_sessions: Dict[str, object] = {}

def get_or_create_chat(session_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    Recupera o crea una sesión de chat con Gemini.
    Retorna (chat_obj, session_id).
    """
    if not client:
        raise Exception("AI Service unavailable (API Key missing)")

    user_context = ""
    history_for_model = []

    if user_id:
        user = get_user_by_id(user_id)
        if user:
            age_context = ""
            if user.get("age"):
                if user["age"] < 18:
                    age_context = "El usuario es adolescente. Usa un tono fresco, amigable y dinámico. Utiliza tambien muchos populismos lingüísticos / expresiones populares de la Costa ecuatoriana, ese hablar bien callejero (ejemplo: Ñaño, ya pues, oe, esta full, etc)."
                elif user["age"] > 60:
                    age_context = "El usuario es un adulto mayor. Sé muy claro, paciente y respetuoso."
                else:
                    age_context = "El usuario es un adulto. Mantén un tono profesional."

            user_context = f"""
            INFORMACIÓN DEL USUARIO:
            - Nombre: {user['first_name']} {user['last_name']}
            - Edad: {user.get('age', 'No especificada')}
            
            GUÍA DE PERSONALIDAD:
            {age_context}
            """
            
            # Cargar historial previo de la BD
            db_history = get_recent_chat_history(user_id, limit=20)
            for msg in db_history:
                history_for_model.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })

    if not session_id or session_id not in chat_sessions:
        print("[GEMINI] 🆕 Creating new chat session...")
        new_session_id = str(uuid.uuid4())
        
        tools = [
            get_supermarket_hour, 
            get_product_location, 
            get_supermarket_details,
            search_products,
            compare_products,
            add_product_to_cart_tool,
            view_cart_tool,
            checkout_cart_tool
        ]
        
        system_instruction = f"""Eres un asistente útil de una tienda de electrónica (NovaShop). 
        
        {user_context}
        
        TU CONTEXTO ACTUAL (ID de Usuario):
        Si el usuario está logueado, su ID es: "{user_id if user_id else 'ANONYMOUS'}"
        IMPORTANTE: SIEMPRE que uses herramientas de carrito (add_product_to_cart_tool, view_cart_tool, checkout_cart_tool),
        DEBES pasar este ID "{user_id if user_id else ''}" como el argumento `user_id`. No preguntes el ID al usuario.

        OBJETIVO PRINCIPAL: AHORRO DE PALABRAS (CRÍTICO)
        - Tu salida se convierte a audio pago. CADA CARÁCTER CUENTA.
        - Sé EXTREMADAMENTE conciso y directo, pero sin olvidar signos de puntuacion.
        - NO saludes si no es el primer mensaje. NO te despidas innecesariamente.
        - Ve al grano. Responde la pregunta y punto, siendo amable pero no tan efusivo.
        - Usa frases cortas. Máximo 1 o 2 oraciones si es posible.
        - Evita palabras de relleno como "Claro que sí", "Por supuesto", "Entiendo", "Me parece genial".
        - Si el usuario pide un producto, di el precio y características clave y ya.
        - EJEMPLO CORRECTO: "El iPhone 15 cuesta 899 dolares y tiene 128 gigas de almacenamiento."
        - EJEMPLO INCORRECTO: "Claro, con gusto te ayudo. El iPhone 15 es un excelente dispositivo que cuesta $899 dólares y cuenta con una capacidad de 128GB."

        REGLAS DE CARRITO:
        1. Para agregar items: Primero BUSCA el producto para obtener su ID exacto (product_id), luego usa `add_product_to_cart_tool`.
        2. Si el usuario quiere "terminar", "pagar" o "comprar el carrito", usa `checkout_cart_tool`.
        3. Si `checkout_cart_tool` falla por stock, sugiere alternativas o pregunta si quiere comprar lo que hay.

        REGLAS DE FORMATO:
        - NO uses asteriscos (**) para negritas ni formato Markdown. Escribe texto plano limpio.
        - Ejemplo INCORRECTO: **Producto**
        - Ejemplo CORRECTO: Producto
        """

        try:
            print(f"[GEMINI] 📜 History loaded: {len(history_for_model)} messages")
            print(f"[GEMINI] 🛠️ Initializing chat with {len(tools)} tools...")
            
            chat = client.chats.create(
                model=MODEL_ID,
                config=types.GenerateContentConfig(
                    tools=tools,
                    system_instruction=system_instruction,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                ),
                history=history_for_model 
            )
            chat_sessions[new_session_id] = chat
            print(f"[GEMINI] ✅ Chat created successfully (ID: {new_session_id})")
            return chat, new_session_id
        except Exception as e:
            print(f"[GEMINI] ⚠️ Error creating chat with {MODEL_ID}: {e}. Trying fallback...")
            try:
                chat = client.chats.create(
                    model=MODEL_FALLBACK,
                    config=types.GenerateContentConfig(
                        tools=tools,
                        system_instruction=system_instruction,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                    ),
                    history=history_for_model
                )
                chat_sessions[new_session_id] = chat
                print(f"[GEMINI] ✅ Fallback Chat created successfully (ID: {new_session_id})")
                return chat, new_session_id
            except Exception as e2:
                 raise Exception(f"Failed to initialize AI model: {e2}")

    print(f"[GEMINI] 🔄 Resuming session: {session_id}")
    return chat_sessions[session_id], session_id
