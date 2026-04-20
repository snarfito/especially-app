/**
 * Especially Frontend — Login.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/auth";

const JADE = "#2E7D60";
const JADE_DARK = "#1C5241";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login({ email, password });
      if (data.user.user_role === "seller" || data.user.user_role === "socio_productor") {
        router.push("/dashboard");
      } else {
        router.push("/catalogo");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex justify-center items-start py-20">
      <div
        className="bg-white rounded-2xl p-8 w-full max-w-sm"
        style={{ border: "1px solid #E5E7EB" }}
      >
        <h1 className="text-2xl font-bold mb-1" style={{ color: "#0F1F19" }}>
          Ingresar
        </h1>
        <p className="text-sm mb-7" style={{ color: "#9CA3AF" }}>
          Bienvenido de nuevo a Especially
        </p>

        {error && (
          <div
            className="text-xs rounded-xl px-4 py-3 mb-5"
            style={{ backgroundColor: "#FEF2F2", color: "#DC2626", border: "1px solid #FCA5A5" }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium" style={{ color: "#374151" }}>
              Correo electrónico
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="tu@correo.com"
              className="w-full px-3 py-2.5 text-sm rounded-xl outline-none transition-colors"
              style={{ border: "1.5px solid #E5E7EB", backgroundColor: "#FAFAFA" }}
              onFocus={e => (e.target.style.borderColor = JADE)}
              onBlur={e => (e.target.style.borderColor = "#E5E7EB")}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium" style={{ color: "#374151" }}>
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full px-3 py-2.5 text-sm rounded-xl outline-none transition-colors"
              style={{ border: "1.5px solid #E5E7EB", backgroundColor: "#FAFAFA" }}
              onFocus={e => (e.target.style.borderColor = JADE)}
              onBlur={e => (e.target.style.borderColor = "#E5E7EB")}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-1 py-2.5 rounded-full text-sm font-semibold text-white transition-colors disabled:opacity-60"
            style={{ backgroundColor: loading ? "#7DCCA8" : JADE }}
            onMouseEnter={e => !loading && (e.currentTarget.style.backgroundColor = JADE_DARK)}
            onMouseLeave={e => !loading && (e.currentTarget.style.backgroundColor = JADE)}
          >
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>

        <p className="text-xs text-center mt-6" style={{ color: "#9CA3AF" }}>
          ¿No tienes cuenta?{" "}
          <Link href="/registro" className="font-semibold" style={{ color: JADE }}>
            Regístrate
          </Link>
        </p>
      </div>
    </div>
  );
}
