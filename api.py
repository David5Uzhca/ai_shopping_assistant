
import os
import uuid
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from google import genai
from google.genai import types

# Import tools
from tools.basic_tools import get_supermarket_hour, get_product_location, get_supermarket_details
from tools.product_tools import search_products, compare_products, process_purchase
from tools.cart_tools import add_product_to_cart_tool, view_cart_tool, checkout_cart_tool

# Import DB Ops
from db.user_ops import create_user, authenticate_user, get_user_by_id
from db.chat_ops import save_chat_message, get_recent_chat_history

# Load environment variables
load_dotenv(".env")

# --- App Configuration ---
app = FastAPI(
    title="AgentLM API",
    description="Backend API for the Supermarket AI Assistant",
    version="1.0.0"
)

# Permitir consumo desde un frontend web/móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gemini Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ADVERTENCIA: GEMINI_API_KEY no encontrada. El chat fallará.")

client = genai.Client(api_key=api_key) if api_key else None
MODEL_ID = "gemini-3-flash-preview"
MODEL_FALLBACK = "gemini-2.0-flash-exp"

# --- Models ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    email: EmailStr
    phone: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: str
    token: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None 

class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_function_call: bool = False

# --- Session Management ---
chat_sessions: Dict[str, object] = {}

# --- Helper Functions ---
def get_or_create_chat(session_id: Optional[str] = None, user_id: Optional[str] = None):
    if not client:
        raise HTTPException(status_code=503, detail="AI Service unavailable (API Key missing)")

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
            # Gemini espera: [{'role': 'user', 'parts': ['texto']}, {'role': 'model', 'parts': ['texto']}]
            db_history = get_recent_chat_history(user_id, limit=20)
            for msg in db_history:
                # role en BD: 'user'/'model'. Google espera 'user'/'model'.
                history_for_model.append({
                    "role": msg["role"],
                    "parts": [msg["content"]]
                })

    if not session_id or session_id not in chat_sessions:
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
        
        system_instruction = f"""Eres un asistente útil de un supermercado (AgentLM). 
        
        {user_context}
        
        TU CONTEXTO ACTUAL (ID de Usuario):
        Si el usuario está logueado, su ID es: "{user_id if user_id else 'ANONYMOUS'}"
        IMPORTANTE: SIEMPRE que uses herramientas de carrito (add_product_to_cart_tool, view_cart_tool, checkout_cart_tool),
        DEBES pasar este ID "{user_id if user_id else ''}" como el argumento `user_id`. No preguntes el ID al usuario.

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
            print(f"Creating new chat with history len: {len(history_for_model)}")
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
            return chat, new_session_id
        except Exception as e:
            print(f"Error creating chat with {MODEL_ID}: {e}. Trying fallback...")
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
                return chat, new_session_id
            except Exception as e2:
                 raise HTTPException(status_code=500, detail=f"Failed to initialize AI model: {e2}")

    return chat_sessions[session_id], session_id

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "AgentLM API is running 🚀"}

@app.post("/auth/register", response_model=UserResponse)
def register(request: RegisterRequest):
    try:
        user_data = request.model_dump()
        user_id = create_user(user_data)
        return UserResponse(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            token="dummy-token-for-now"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Register Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno.")

@app.post("/auth/login", response_model=UserResponse)
def login(request: LoginRequest):
    try:
        user = authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")
        return UserResponse(
            user_id=str(user["user_id"]),
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            token="dummy-token-for-now"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno.")

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        chat, session_id = get_or_create_chat(request.session_id, request.user_id)
        
        # Enviar mensaje
        response = chat.send_message(request.message)
        text_response = response.text if response.text else "(Sin respuesta...)"
        
        # Guardar en historial persistente si hay usuario logueado
        if request.user_id:
            try:
                save_chat_message(request.user_id, "user", request.message, session_id)
                save_chat_message(request.user_id, "model", text_response, session_id)
            except Exception as db_e:
                print(f"Error saving chat history: {db_e}")

        return ChatResponse(response=text_response, session_id=session_id)
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

_frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(_frontend_dist):
    app.mount("/app", StaticFiles(directory=_frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


_frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(_frontend_dist):
    app.mount("/app", StaticFiles(directory=_frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
