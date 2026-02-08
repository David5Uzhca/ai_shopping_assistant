import strawberry
from typing import Optional
from services.gemini_service import get_or_create_chat
from db.chat_ops import save_chat_message
from db.user_ops import create_user, authenticate_user

from services.elevenlabs_service import generate_voice_audio

@strawberry.type
class ChatResponseType:
    response: str
    session_id: str
    audio: Optional[str] = None

@strawberry.type
class UserType:
    user_id: str
    first_name: str
    last_name: str
    email: str
    token: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from AgentLM GraphQL!"

@strawberry.type
class Mutation:
    @strawberry.mutation
    def chat(
        self, 
        message: str, 
        session_id: Optional[str] = None, 
        user_id: Optional[str] = None,
        generate_audio: bool = False
    ) -> ChatResponseType:
        print(f"\n[GRAPHQL] 🚀 Chat mutation received. Message start: '{message[:50]}...' | Session: {session_id} | User: {user_id}")
        try:
            # 1. Obtener respuesta de texto (Gemini)
            chat_obj, real_session_id = get_or_create_chat(session_id, user_id)
            
            print(f"[GRAPHQL] 🧠 Sending message to Gemini Service...")
            gemini_resp = chat_obj.send_message(message)
            text_response = gemini_resp.text if gemini_resp.text else "(Sin respuesta...)"
            print(f"[GRAPHQL] 🤖 Gemini response received: '{text_response[:50]}...'")
            
            # 2. Generar Audio (ElevenLabs) si se solicita
            audio_base64 = None
            if generate_audio:
                print(f"[GRAPHQL] 🔊 Audio generation requested. Calling ElevenLabs...")
                # Usar solo la primera oración o dos para no gastar tanto crédito y ser rápido
                # O enviar todo si es corto.
                audio_base64 = generate_voice_audio(text_response)
                status = "✅ Generated" if audio_base64 else "❌ Failed/Empty"
                print(f"[GRAPHQL] {status} Audio. Length: {len(audio_base64) if audio_base64 else 0} chars")

            # 3. Persistir historial
            if user_id:
                print(f"[GRAPHQL] 💾 Saving chat history to DB...")
                try:
                    save_chat_message(user_id, "user", message, real_session_id)
                    save_chat_message(user_id, "model", text_response, real_session_id)
                except Exception as e:
                    print(f"[GRAPHQL] ⚠️ Error saving history: {e}")
            
            print(f"[GRAPHQL] 🏁 Chat mutation finished. Returning response.\n")
            return ChatResponseType(
                response=text_response, 
                session_id=real_session_id,
                audio=audio_base64
            )
        except Exception as e:
            print(f"[GRAPHQL] ❌ CRITICAL ERROR: {str(e)}")
            raise Exception(str(e))

    @strawberry.mutation
    def login(self, email: str, password: str) -> UserType:
        user = authenticate_user(email, password)
        if not user:
            raise Exception("Credenciales inválidas")
        
        return UserType(
            user_id=str(user["user_id"]),
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            token="dummy-token-for-now"
        )

    @strawberry.mutation
    def register(
        self, 
        first_name: str, 
        last_name: str, 
        email: str, 
        password: str,
        age: int,
        gender: str,
        phone: str
    ) -> UserType:
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "age": age,
            "gender": gender,
            "phone": phone
        }
        try:
            user_id = create_user(user_data)
            return UserType(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                token="dummy-token-for-now"
            )
        except Exception as e:
            raise Exception(str(e))

schema = strawberry.Schema(query=Query, mutation=Mutation)
