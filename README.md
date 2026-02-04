# NovaShop (AgentLM) - Asistente de Supermercado con IA

Este proyecto implementa un asistente virtual inteligente para un supermercado, capaz de interactuar con usuarios mediante texto y **voz**, gestionar carritos de compras, buscar productos y mantener una memoria persistente de las conversaciones. Utiliza **Google Gemini** como cerebro y **FastAPI** + **React** para la infraestructura.

## Tabla de Contenidos
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Características Principales](#características-principales)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Configuración y Ejecución](#configuración-y-ejecución)
6. [Base de Datos](#base-de-datos)

---

## Arquitectura del Sistema

El sistema sigue una arquitectura cliente-servidor moderna:

- **Frontend**: Aplicación **React** (Vite + TypeScript) que maneja la interfaz de usuario, captura de audio (Web Speech API) y comunicación con el backend.
- **Backend**: API RESTful construida con **FastAPI** (Python). Actúa como orquestador entre el usuario, la base de datos y el modelo de IA.
- **AI Core**: Integración con **Google Gemini 2.0 Flash** (o versiones superiores) utilizando *Function Calling* para ejecutar herramientas reales (consultar precios, stock, agregar al carrito).
- **Base de Datos**: **PostgreSQL** para persistencia de usuarios, inventario, carritos de compra e historial de chat.

---

## Tecnologías Utilizadas

### Backend
- **Python 3.10+**
- **FastAPI**: Framework web de alto rendimiento.
- **Google GenAI SDK**: Para la interacción con modelos Gemini.
- **Psycopg2**: Adaptador de base de datos PostgreSQL.
- **Pydantic**: Validación de datos.
- **Uvicorn**: Servidor ASGI.

### Frontend
- **React 18**
- **TypeScript**
- **Vite**: Build tool.
- **CSS Modules / Vanilla CSS**: Estilizado personalizado y "glassmorphism".
- **Web Speech API**: Reconocimiento y síntesis de voz nativa del navegador.

### Datos
- **PostgreSQL**: Motor de base de datos relacional.

---

## Características Principales

1.  **Chatbot Conversacional**: Interfaz de chat natural con memoria a largo plazo (los mensajes se guardan en BD y se recargan al iniciar sesión).
2.  **Interacción por Voz (Voice Mode)**:
    -   Activación mediante comandos ("hablemos directamente") o botón dedicado.
    -   Avatar animado (ShopiBOT) con estados visuales (escuchando, pensando, hablando).
    -   Respuestas habladas automáticas.
3.  **Gestión de Inventario y Ventas**:
    -   Consulta de productos en tiempo real (precio, stock, ubicación).
    -   Comparación de productos (generación de tablas comparativas).
4.  **Carrito de Compras Inteligente**:
    -   El usuario puede decir "agrega dos coca colas" y la IA detecta el producto, verifica stock y lo agrega.
    -   Checkout y actualización de inventario.
5.  **Personalidad Adaptativa**:
    -   El agente adapta su tono según la edad del usuario (ej. jerga local para jóvenes, tono formal para adultos).

---

## Estructura del Proyecto

```
agent_lm/
├── api.py                  # Punto de entrada del Backend (FastAPI app)
├── .env                    # Variables de entorno (API Keys, DB creds)
├── db/                     # Lógica de Base de Datos
│   ├── connection.py       # Pool de conexiones PostgreSQL
│   ├── user_ops.py         # CRUD de Usuarios
│   ├── chat_ops.py         # Persistencia de historial de chat
│   └── scripts_sql/        # Scripts de creación de tablas
├── tools/                  # Herramientas para la IA (Function Calling)
│   ├── product_tools.py    # Búsqueda y comparación de productos
│   ├── cart_tools.py       # Lógica del carrito de compras
│   └── basic_tools.py      # Información general del local
└── frontend/               # Aplicación React
    ├── src/
    │   ├── ui/             # Componentes (App, VoiceChat, Login)
    │   └── lib/            # Cliente API
    └── public/             # Assets (imágenes del robot)
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
