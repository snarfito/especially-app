/**
 * Especially Frontend — Página de Registro.
 *
 * Formulario de creación de cuenta con selección de rol:
 * - Comprador
 * - Socio Productor
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { login } from "@/lib/auth";
import type { UserRole } from "@/types";

export default function RegistroPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [role, setRole] = useState<UserRole>("comprador");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/users/", { full_name: fullName, email, password, role });
      const data = await login({ email, password });
      if (data.user.role === "socio_productor") {
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
    <div className="flex justify-center items-start py-16">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Crear cuenta</h1>
        <p className="text-sm text-gray-500 mb-6">Únete a Especially</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-jade-400"
              placeholder="Tu nombre"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              placeholder="tu@correo.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              placeholder="Mínimo 8 caracteres"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Soy...</label>
            <div className="flex gap-3">
              {(["comprador", "socio_productor"] as UserRole[]).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className={`flex-1 py-2 rounded-lg border text-sm font-medium transition-colors ${
                    role === r
                      ? "border-jade-500 bg-jade-50 text-jade-600"
                      : "border-gray-300 text-gray-600 hover:border-jade-300"
                  }`}
                >
                  {r === "comprador" ? "Comprador" : "Socio Productor"}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-jade-500 text-white py-2.5 rounded-full font-medium hover:bg-jade-600 transition-colors disabled:opacity-60 mt-2"
          >
            {loading ? "Creando cuenta..." : "Crear cuenta"}
          </button>
        </form>

        <p className="text-sm text-gray-500 text-center mt-6">
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="text-jade-600 font-medium hover:underline">
            Ingresar
          </Link>
        </p>
      </div>
    </div>
  );
}
