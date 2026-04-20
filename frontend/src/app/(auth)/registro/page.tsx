/**
 * Especially Frontend — Registro.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { login } from "@/lib/auth";

const JADE = "#2E7D60";
const JADE_DARK = "#1C5241";
const JADE_LIGHT = "#E6F4EE";

export default function RegistroPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"buyer" | "seller">("buyer");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/users", { full_name: fullName, email, password, user_role: role });
      const data = await login({ email, password });
      if (data.user.user_role === "seller" || data.user.user_role === "socio_productor") {
        router.push("/dashboard");
      } else {
        router.push("/catalogo");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la cuenta");
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
          Crear cuenta
        </h1>
        <p className="text-sm mb-7" style={{ color: "#9CA3AF" }}>
          Únete a Especially
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
              Nombre completo
            </label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder="Tu nombre"
              className="w-full px-3 py-2.5 text-sm rounded-xl outline-none"
              style={{ border: "1.5px solid #E5E7EB", backgroundColor: "#FAFAFA" }}
              onFocus={e => (e.target.style.borderColor = JADE)}
              onBlur={e => (e.target.style.borderColor = "#E5E7EB")}
            />
          </div>

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
              className="w-full px-3 py-2.5 text-sm rounded-xl outline-none"
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
              minLength={8}
              placeholder="Mínimo 8 caracteres"
              className="w-full px-3 py-2.5 text-sm rounded-xl outline-none"
              style={{ border: "1.5px solid #E5E7EB", backgroundColor: "#FAFAFA" }}
              onFocus={e => (e.target.style.borderColor = JADE)}
              onBlur={e => (e.target.style.borderColor = "#E5E7EB")}
            />
          </div>

          {/* Rol */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-medium" style={{ color: "#374151" }}>
              Soy...
            </label>
            <div className="flex gap-2">
              {(["buyer", "seller"] as const).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className="flex-1 py-2 rounded-xl text-sm font-medium transition-all"
                  style={{
                    border: `1.5px solid ${role === r ? JADE : "#E5E7EB"}`,
                    backgroundColor: role === r ? JADE_LIGHT : "white",
                    color: role === r ? JADE_DARK : "#6B7280",
                  }}
                >
                  {r === "buyer" ? "Comprador" : "Socio Productor"}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-1 py-2.5 rounded-full text-sm font-semibold text-white transition-colors disabled:opacity-60"
            style={{ backgroundColor: loading ? "#7DCCA8" : JADE }}
            onMouseEnter={e => !loading && (e.currentTarget.style.backgroundColor = JADE_DARK)}
            onMouseLeave={e => !loading && (e.currentTarget.style.backgroundColor = JADE)}
          >
            {loading ? "Creando cuenta..." : "Crear cuenta"}
          </button>
        </form>

        <p className="text-xs text-center mt-6" style={{ color: "#9CA3AF" }}>
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="font-semibold" style={{ color: JADE }}>
            Ingresar
          </Link>
        </p>
      </div>
    </div>
  );
}
