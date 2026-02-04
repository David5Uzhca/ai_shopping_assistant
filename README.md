# NovaShop (AgentLM) - Asistente de Supermercado con IA

Este proyecto implementa un asistente virtual inteligente para un supermercado, capaz de interactuar con usuarios mediante texto y **voz**, gestionar carritos de compras, buscar productos y mantener una memoria persistente de las conversaciones. Utiliza **Google Gemini** como cerebro, **FastAPI + GraphQL** para la infraestructura.

## Tabla de Contenidos
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Características Principales](#características-principales)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Configuración y Ejecución](#configuración-y-ejecución)
6. [GraphQL API](#graphql-api)

---

## Arquitectura del Sistema

El sistema sigue una arquitectura moderna orientada a servicios y GraphQL:

- **Frontend**: Aplicación **React** (Vite + TypeScript) que consume una única API GraphQL.
- **Backend**: Servidor **FastAPI** que monta un endpoint GraphQL (`/graphql`) usando **Strawberry**.
- **AI Core**: Servicio centralizado (`GeminiService`) que gestiona sesiones, historial y llamadas a herramientas (precios, stock).
- **Base de Datos**: **PostgreSQL** para persistencia de usuarios, inventario, carritos e historial de chat.

---

## Tecnologías Utilizadas

### Backend
- **Python 3.10+**
- **FastAPI**: Servidor web.
- **Strawberry GraphQL**: Framework para definir el esquema y resolutores.
- **Google GenAI SDK**: Integración con Gemini.
- **Psycopg2**: Conexión a BD.
- **Uvicorn**: Servidor ASGI.

### Frontend
- **React 18** + **TypeScript**.
- **Apollo Client / Fetch**: Para realizar queries y mutaciones.
- **Web Speech API**: Voz nativa.

### Datos
- **PostgreSQL**: Motor de base de datos relacional.

---

## Características Principales

1.  **Arquitectura 100% GraphQL**:
    -   Un único endpoint (`/graphql`) para autenticación, chat y operaciones.
    -   Tipado fuerte y esquemas claros.
2.  **Chatbot Conversacional con Memoria**:
    -   El agente recuerda conversaciones pasadas gracias a la persistencia en BD.
    -   Personalidad adaptable según el perfil del usuario (edad, ubicación).
3.  **Interacción por Voz (ShopiBOT)**:
    -   Avatar animado con estados reactivos.
    -   Control por voz completo (Speech-to-Text y Text-to-Speech).
4.  **Gestión Inteligente**:
    -   Búsqueda de productos, comparación de precios y gestión de carritos mediante *Function Calling*.

---

## Estructura del Proyecto

```
agent_lm/
├── api.py                  # Entry Point. Monta Strawberry GraphQL.
├── graphql_schema.py       # Definición de Tipos (Query, Mutation, UserType).
├── services/
│   └── gemini_service.py   # Lógica conversacional y gestión de sesiones AI.
├── db/                     # Capa de datos (Usuarios, Chat, Carrito).
├── tools/                  # Herramientas para la IA (Function Calling).
├── frontend/               # Aplicación React consumiendo GraphQL.
└── .env                    # Configuración.
```

---

## GraphQL API

El backend expone un playground interactivo en `http://localhost:8000/graphql`.

### Ejemplos de Mutaciones

**1. Iniciar Conversación (Chat):**
```graphql
mutation {
  chat(
    message: "Hola, necesito leche deslactosada", 
    userId: "UUID-DEL-USUARIO"
  ) {
    response
    sessionId
  }
}
```

**2. Iniciar Sesión:**
```graphql
mutation {
  login(email: "juan@example.com", password: "123") {
    userId
    firstName
    token
  }
}
```

---

## Configuración y Ejecución

### Prerrequisitos
- Python instalado.
- Node.js instalado.
- Servidor PostgreSQL corriendo.
- API Key de Google Gemini.

### 1. Configuración del Backend

1.  Crear entorno virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```
2.  Instalar dependencias:
    ```bash
    pip install fastapi uvicorn google-genai python-dotenv psycopg2
    ```
3.  Configurar variables de entorno:
    Crea un archivo `.env` en la raíz con:
    ```env
    GEMINI_API_KEY=tu_api_key_aqui
    DB_HOST=localhost
    DB_NAME=supermercado_db
    DB_USER=postgres
    DB_PASSWORD=tu_password
    ```
4.  Ejecutar servidor:
    ```bash
    python api.py
    ```
    *El servidor correrá en `http://localhost:8000`*

### 2. Configuración del Frontend

1.  Navegar a la carpeta frontend:
    ```bash
    cd frontend
    ```
2.  Instalar dependencias:
    ```bash
    npm install
    ```
3.  Ejecutar entorno de desarrollo:
    ```bash
    npm run dev
    ```
    *La web estará disponible en `http://localhost:5173` (o similar).*

---

## Base de Datos

Asegúrate de ejecutar los scripts SQL ubicados en `db/` en tu base de datos PostgreSQL para crear las tablas necesarias:

1.  `create_users_table.sql` (Usuarios)
2.  `create_cart_table.sql` (Carrito)
3.  `create_chat_history.sql` (Historial de Conversación)
4.  *(Opcional)* Tabla de productos e inventario (según tu esquema local).

---

## Autores
Juan David Uzhca\
Domenika Sofia Delgado\
Irar Nankamai

Desarrollado como parte del proyecto de Agentes Avanzados (AgentLM / NovaShop).
