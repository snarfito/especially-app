/**
 * Especially Frontend — Componente Navbar.
 *
 * Barra de navegación principal. Muestra links según el rol del usuario.
 * Se adapta entre sesión iniciada y no iniciada.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { useEffect, useState } from "react";
import type { User } from "@/types";

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getCurrentUser());
  }, []);

  function handleLogout() {
    logout();
    setUser(null);
    router.push("/login");
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      {/* Logo */}
      <Link href="/" className="text-xl font-bold text-jade-600 tracking-tight">
        Especially
      </Link>

      {/* Links centrales */}
      <div className="flex gap-6 text-sm font-medium text-gray-600">
        <Link href="/catalogo" className="hover:text-jade-600 transition-colors">
          Catálogo
        </Link>
        {user?.role === "socio_productor" && (
          <Link href="/dashboard" className="hover:text-jade-600 transition-colors">
            Dashboard
          </Link>
        )}
      </div>

      {/* Auth */}
      <div className="flex items-center gap-4 text-sm">
        {user ? (
          <>
            <span className="text-gray-500">Hola, {user.full_name.split(" ")[0]}</span>
            <button
              onClick={handleLogout}
              className="text-gray-600 hover:text-red-500 transition-colors"
            >
              Salir
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="text-gray-600 hover:text-jade-600 transition-colors">
              Ingresar
            </Link>
            <Link
              href="/registro"
              className="bg-jade-500 text-white px-4 py-1.5 rounded-full hover:bg-jade-600 transition-colors"
            >
              Registrarse
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
