import strawberry
from typing import Optional
from services.gemini_service import get_or_create_chat
from db.chat_ops import save_chat_message
from db.user_ops import create_user, authenticate_user

@strawberry.type
class ChatResponseType:
    response: str
    session_id: str

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
    def chat(self, message: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ChatResponseType:
        try:
            chat, real_session_id = get_or_create_chat(session_id, user_id)
            
            # Send message to Gemini
            response = chat.send_message(message)
            text_response = response.text if response.text else "(Sin respuesta...)"
            
            # Persist history
            if user_id:
                try:
                    save_chat_message(user_id, "user", message, real_session_id)
                    save_chat_message(user_id, "model", text_response, real_session_id)
                except Exception as e:
                    print(f"Error saving history: {e}")
            
            return ChatResponseType(response=text_response, session_id=real_session_id)
        except Exception as e:
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
