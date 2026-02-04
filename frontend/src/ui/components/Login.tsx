

import { useState } from "react";
import { loginUser } from "../../lib/api";

interface LoginProps {
    onLogin: (user: any) => void;
    onGoToRegister: () => void;
}

export function Login({ onLogin, onGoToRegister }: LoginProps) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const user = await loginUser(email, password);
            onLogin(user);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="authContainer">
            <div className="authCard">
                <h2 className="authTitle">Bienvenido</h2>
                <p className="authSubtitle">Inicia sesión para continuar</p>

                {error && <div className="errorBox" style={{ textAlign: "center" }}>{error}</div>}

                <form className="authForm" onSubmit={handleSubmit}>
                    <div className="formGroup">
                        <label>Correo Electrónico</label>
                        <input
                            type="email"
                            placeholder="tu@correo.com"
                            className="input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="formGroup">
                        <label>Contraseña</label>
                        <input
                            type="password"
                            placeholder="••••••••"
                            className="input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btnPrimary fullWidth" disabled={loading}>
                        {loading ? "Iniciando..." : "Iniciar"}
                    </button>
                </form>

                <div className="authFooter">
                    <a href="#" className="link muted">
                        ¿Olvidaste tu contraseña?
                    </a>
                    <button onClick={onGoToRegister} className="link btnLink" disabled={loading}>
                        ¿No tienes cuenta aún? Únetenos ahora
                    </button>
                </div>
            </div>
        </div>
    );
}
