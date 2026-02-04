
// Base API URL
// Detecta automáticamente la IP si estás en LAN (ej: 192.168.x.x)
const API_URL = `http://${window.location.hostname}:8000/graphql`;

// --- Types ---

export interface LoginResponse {
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  token?: string;
}

export interface RegisterRequest {
  first_name: string;
  last_name: string;
  gender: string;
  age: number;
  email: string;
  phone: string;
  password: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string | null;
  user_id?: string | null;
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

// --- Helper Functions ---

async function graphqlRequest(query: string) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  const json = await res.json();

  if (json.errors) {
    throw new Error(json.errors[0].message || "Error en GraphQL");
  }

  return json.data;
}

// --- Auth Functions ---

export async function loginUser(email: string, password: string): Promise<LoginResponse> {
  const mutation = `
    mutation {
      login(email: "${email}", password: "${password}") {
        userId
        firstName
        lastName
        email
        token
      }
    }
  `;

  const data = await graphqlRequest(mutation);
  // Mapeamos resp camelCase a snake_case si la interfaz lo requiere, 
  // pero el frontend usa lo que definimos aqui. 
  // Ajustamos LoginResponse del frontend si fuera necesario, 
  // pero mantendré compatibilidad con el resto de la app

  // OJO: Strawberry devuelve campos en camelCase por defecto (userId, firstName...)
  const u = data.login;
  return {
    user_id: u.userId,
    first_name: u.firstName,
    last_name: u.lastName,
    email: u.email,
    token: u.token
  };
}

export async function registerUser(data: RegisterRequest): Promise<LoginResponse> {
  // Aseguramos que edad sea número
  const age = Number(data.age);

  const mutation = `
    mutation {
      register(
        firstName: "${data.first_name}",
        lastName: "${data.last_name}",
        email: "${data.email}",
        password: "${data.password}",
        age: ${age},
        gender: "${data.gender}",
        phone: "${data.phone}"
      ) {
        userId
        firstName
        lastName
        email
        token
      }
    }
  `;

  const respData = await graphqlRequest(mutation);
  const u = respData.register;

  return {
    user_id: u.userId,
    first_name: u.firstName,
    last_name: u.lastName,
    email: u.email,
    token: u.token
  };
}

// --- Chat Functions ---

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  // Manejo de valores nulos para el string interpolation
  const sessionIdArg = payload.session_id ? `"${payload.session_id}"` : "null";
  const userIdArg = payload.user_id ? `"${payload.user_id}"` : "null";

  // Limpiamos el mensaje de comillas dobles que rompan la query
  const safeMessage = payload.message.replace(/"/g, '\\"').replace(/\n/g, "\\n");

  const mutation = `
    mutation {
      chat(
        message: "${safeMessage}",
        sessionId: ${sessionIdArg},
        userId: ${userIdArg}
      ) {
        response
        sessionId
      }
    }
  `;

  const data = await graphqlRequest(mutation);
  return {
    response: data.chat.response,
    session_id: data.chat.sessionId // Strawberry camelCase
  };
}


