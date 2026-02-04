
// Base API URL
// Base API URL
// Detecta automáticamente la IP si estás en LAN (ej: 192.168.x.x)
const API_URL = `http://${window.location.hostname}:8000`;

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
  user_id?: string | null; // Nuevo campo para contexto
}

export interface ChatResponse {
  response: string;
  session_id: string;
}

// --- Auth Functions ---

export async function loginUser(email: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al iniciar sesión");
  }

  return res.json();
}

export async function registerUser(data: RegisterRequest): Promise<LoginResponse> {
  // Aseguramos que edad sea número
  const payload = { ...data, age: Number(data.age) };

  const res = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al registrarse");
  }

  return res.json();
}

// --- Chat Functions ---

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Error en el servidor");
  }

  return res.json();
}


