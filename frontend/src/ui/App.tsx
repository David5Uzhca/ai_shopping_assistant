
import { useEffect, useMemo, useRef, useState } from "react";
import { sendChatMessage } from "../lib/api";
import { Login } from "./components/Login";
import { Register } from "./components/Register";
import { VoiceChat } from "./components/VoiceChat";

type Msg = { role: "user" | "assistant"; text: string };
type ViewState = "login" | "register" | "chat" | "voice";

const SESSION_KEY = "agentlm.session_id";

export function App() {
  // Navigation State
  const [view, setView] = useState<ViewState>("login");

  // User State
  const [user, setUser] = useState<any | null>(null);

  // Chat State
  const [sessionId, setSessionId] = useState<string | null>(() => {
    return localStorage.getItem(SESSION_KEY);
  });
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "assistant",
      text: "Hola, soy tu asistente del supermercado. ¿En qué te ayudo?"
    }
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(SESSION_KEY, sessionId ?? "");
  }, [sessionId]);

  useEffect(() => {
    // Auto-scroll al final
    const el = listRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages, isSending, view]);

  const canSend = useMemo(() => input.trim().length > 0 && !isSending, [input, isSending]);

  // Auth Handlers
  const handleAuthSuccess = (userData: any) => {
    setUser(userData);
    setView("chat");
    // Personalizar saludo inicial si es nueva sesión o si el chat estaba vacío/default
    if (!sessionId || messages.length <= 1) {
      setMessages([{
        role: "assistant",
        text: `Hola ${userData.first_name}, soy tu asistente del supermercado. ¿En qué te ayudo hoy?`
      }]);
    }
  };

  function onLogout() {
    setUser(null);
    setSessionId(null);
    localStorage.removeItem(SESSION_KEY);
    setView("login");
    setMessages([{
      role: "assistant",
      text: "Hola, soy tu asistente del supermercado. ¿En qué te ayudo?"
    }]);
  }

  async function onSend() {
    const text = input.trim();
    if (!text || isSending) return;

    // Activación por voz (Triggers)
    if (["hablemos directamente", "conversemos"].includes(text.toLowerCase())) {
      setInput("");
      setView("voice");
      return;
    }

    setError(null);
    setIsSending(true);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);

    try {
      const res = await sendChatMessage({
        message: text,
        session_id: sessionId,
        user_id: user?.user_id // Enviamos el ID para que le API personalice
      });
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", text: res.response }]);
    } catch (e: any) {
      setError(e?.message ?? "Error desconocido");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Tuve un problema hablando con el servidor. Reintenta en unos segundos."
        }
      ]);
    } finally {
      setIsSending(false);
    }
  }

  function onResetSession() {
    setSessionId(null);
    localStorage.removeItem(SESSION_KEY);
    setMessages([
      {
        role: "assistant",
        text: user ? `Sesión reiniciada, ${user.first_name}. ¿Qué necesitas ahora?` : "Sesión reiniciada. ¿Qué necesitas ahora?"
      }
    ]);
    setError(null);
  }

  // --- Render Views ---

  if (view === "login") {
    return (
      <div className="shell">
        <Login
          onLogin={handleAuthSuccess}
          onGoToRegister={() => setView("register")}
        />
      </div>
    );
  }

  if (view === "register") {
    return (
      <div className="shell">
        <Register
          onCancel={() => setView("login")}
          onRegister={handleAuthSuccess}
        />
      </div>
    );
  }

  if (view === "voice") {
    return (
      <VoiceChat
        sessionId={sessionId}
        user={user}
        onClose={() => setView("chat")}
        onUpdateSession={(sid) => setSessionId(sid)}
      />
    );
  }

  // Chat Interface (Default)
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="logo">N</div>
          <div className="brandText">
            <div className="title">NovaShop</div>
            <div className="subtitle">LLM Agent + Tools (Supermercado)</div>
          </div>
        </div>
        <div className="actions" style={{ display: "flex", gap: "10px" }}>
          <button className="btn btnSecondary" onClick={onResetSession} type="button">
            Nueva sesión
          </button>
          <button className="btn btnSecondary" onClick={onLogout} type="button" style={{ borderColor: "rgba(239, 68, 68, 0.5)", color: "#ef4444" }}>
            Salir
          </button>
        </div>
      </header>

      <main className="main">
        <div className="card">
          <div className="messages" ref={listRef} aria-live="polite">
            {messages.map((m, idx) => (
              <div key={idx} className={`msgRow ${m.role}`}>
                <div className="bubble">
                  <div className="role">{m.role === "user" ? "Tú" : "Asistente"}</div>
                  <div className="text">{m.text}</div>
                </div>
              </div>
            ))}

            {isSending && (
              <div className="msgRow assistant">
                <div className="bubble">
                  <div className="role">Asistente</div>
                  <div className="text muted">Pensando…</div>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="errorBox" role="alert">
              {error}
            </div>
          )}

          <div className="composer">
            <input
              className="input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje…"
              onKeyDown={(e) => {
                if (e.key === "Enter") onSend();
              }}
              disabled={isSending}
              aria-label="Mensaje"
            />

            {/* Voice Button within Composer */}
            <button className="btn" onClick={onSend} disabled={!canSend} type="button">
              Enviar
            </button>

            <button
              type="button"
              className="btn btnIcon"
              onClick={() => setView("voice")}
              title="Hablar con el asistente"
              style={{ padding: "0 10px", display: "flex", alignItems: "center", justifyContent: "center", minWidth: "50px" }}
            >
              <img src="/pet/Init.png" alt="Voice" style={{ height: "30px", width: "auto" }} />
            </button>

          </div>

          <div className="footer">
            <div className="meta">
              <span className="pill">
                session_id: <code>{sessionId ? sessionId.slice(0, 8) : "—"}</code>
              </span>
              {user && (
                <span className="pill" style={{ borderColor: "var(--brand)" }}>
                  👤 {user.first_name}
                </span>
              )}
            </div>
            <div className="hint">
              Prueba: “hablemos directamente” · “conversemos”
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}


