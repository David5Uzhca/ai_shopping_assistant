
import { useState } from "react";
import { registerUser } from "../../lib/api";

interface RegisterProps {
    onCancel: () => void;
    onRegister: (user: any) => void;
}

export function Register({ onCancel, onRegister }: RegisterProps) {
    // Form State
    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        gender: "",
        age: "",
        email: "",
        phone: "",
        password: "",
        confirmPassword: ""
    });

    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        // Validaciones básicas
        if (formData.password !== formData.confirmPassword) {
            setError("Las contraseñas no coinciden");
            return;
        }
        if (!formData.gender) {
            setError("Por favor selecciona tu género");
            return;
        }

        setLoading(true);

        try {
            // Llamada al backend
            const user = await registerUser({
                first_name: formData.first_name,
                last_name: formData.last_name,
                gender: formData.gender,
                age: Number(formData.age), // Convertir a número
                email: formData.email,
                phone: formData.phone,
                password: formData.password
            });

            onRegister(user);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="authContainer">
            <div className="authCard large">
                <h2 className="authTitle">Crear Cuenta</h2>
                <p className="authSubtitle">Únete a nosotros hoy mismo</p>

                {error && <div className="errorBox" style={{ textAlign: "center" }}>{error}</div>}

                <form className="authForm grid" onSubmit={handleSubmit}>
                    <div className="formGroup">
                        <label>Nombre</label>
                        <input
                            name="first_name" required
                            value={formData.first_name} onChange={handleChange}
                            type="text" className="input" placeholder="Tu nombre"
                        />
                    </div>
                    <div className="formGroup">
                        <label>Apellido</label>
                        <input
                            name="last_name" required
                            value={formData.last_name} onChange={handleChange}
                            type="text" className="input" placeholder="Tu apellido"
                        />
                    </div>

                    <div className="formGroup">
                        <label>Sexo</label>
                        <select name="gender" className="input" value={formData.gender} onChange={handleChange} required>
                            <option value="">Selecciona...</option>
                            <option value="m">Masculino</option>
                            <option value="f">Femenino</option>
                            <option value="o">Otro</option>
                        </select>
                    </div>
                    <div className="formGroup">
                        <label>Edad</label>
                        <input
                            name="age" required min="10" max="120"
                            value={formData.age} onChange={handleChange}
                            type="number" className="input" placeholder="Ej: 25"
                        />
                    </div>

                    <div className="formGroup full">
                        <label>Correo Electrónico</label>
                        <input
                            name="email" required
                            value={formData.email} onChange={handleChange}
                            type="email" className="input" placeholder="correo@ejemplo.com"
                        />
                    </div>

                    <div className="formGroup full">
                        <label>Celular</label>
                        <input
                            name="phone" required
                            value={formData.phone} onChange={handleChange}
                            type="tel" className="input" placeholder="+1 234 567 890"
                        />
                    </div>

                    <div className="formGroup">
                        <label>Contraseña</label>
                        <input
                            name="password" required minLength={6}
                            value={formData.password} onChange={handleChange}
                            type="password" className="input" placeholder="••••••••"
                        />
                    </div>
                    <div className="formGroup">
                        <label>Verificar Contraseña</label>
                        <input
                            name="confirmPassword" required minLength={6}
                            value={formData.confirmPassword} onChange={handleChange}
                            type="password" className="input" placeholder="••••••••"
                        />
                    </div>

                    <div className="buttonGroup full">
                        <button type="button" onClick={onCancel} className="btn btnSecondary" disabled={loading}>
                            Cancelar
                        </button>
                        <button type="submit" className="btn btnPrimary" disabled={loading}>
                            {loading ? "Creando..." : "Aceptar"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
