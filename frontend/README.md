## AgentLM Frontend (React)

### Desarrollo local

1) Levanta el backend:

```bash
python api.py
```

2) Levanta el frontend:

```bash
cd frontend
npm install
npm run dev
```

El frontend usa **proxy** de Vite hacia `http://localhost:8000`, así que llama a `/chat` sin configurar nada extra.

### Configuración (opcional)

- `VITE_API_BASE_URL`: base URL del backend en producción (por ejemplo `https://tu-dominio.com`).


