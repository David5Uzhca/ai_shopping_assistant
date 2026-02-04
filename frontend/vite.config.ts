import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En dev, proxy para evitar problemas de CORS y mantener URLs limpias.
// El frontend llamará a /chat y Vite lo redirige a http://localhost:8000/chat
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/chat": "http://localhost:8000",
      "/health": "http://localhost:8000"
    }
  }
});


