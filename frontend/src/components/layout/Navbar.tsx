/**
 * Especially Frontend — Navbar.
 * Estilo alineado con AI Studio: fondo blanco, borde sutil, logo jade profundo.
 */

"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { useEffect, useState } from "react";
import type { User } from "@/types";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getCurrentUser());
  }, [pathname]);

  function handleLogout() {
    logout();
    setUser(null);
    router.push("/login");
  }

  const isSeller = user?.user_role === "seller" || user?.user_role === "socio_productor";

  return (
    <nav className="bg-white border-b border-gray-200 px-8 py-0 flex items-center justify-between h-14 sticky top-0 z-40">
      {/* Logo */}
      <Link
        href="/"
        className="text-xl font-bold tracking-tight"
        style={{ color: "#2E7D60" }}
      >
        Especially
      </Link>

      {/* Links centrales */}
      <div className="flex gap-8 text-sm font-medium text-gray-500">
        <Link
          href="/catalogo"
          className="py-4 border-b-2 transition-colors hover:text-gray-900"
          style={{
            borderColor: pathname === "/catalogo" ? "#2E7D60" : "transparent",
            color: pathname === "/catalogo" ? "#2E7D60" : undefined,
          }}
        >
          Catálogo
        </Link>
        {isSeller && (
          <Link
            href="/dashboard"
            className="py-4 border-b-2 transition-colors hover:text-gray-900"
            style={{
              borderColor: pathname === "/dashboard" ? "#2E7D60" : "transparent",
              color: pathname === "/dashboard" ? "#2E7D60" : undefined,
            }}
          >
            Dashboard
          </Link>
        )}
      </div>

      {/* Auth */}
      <div className="flex items-center gap-3 text-sm">
        {user ? (
          <>
            <span className="text-gray-400 text-xs">
              {user.full_name.split(" ")[0]}
            </span>
            <button
              onClick={handleLogout}
              className="text-xs text-gray-500 border border-gray-200 px-3 py-1.5 rounded-full hover:border-gray-400 hover:text-gray-800 transition-colors"
            >
              Salir
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Ingresar
            </Link>
            <Link
              href="/registro"
              className="text-sm text-white px-4 py-1.5 rounded-full font-medium transition-colors"
              style={{ backgroundColor: "#2E7D60" }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = "#1C5241")}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = "#2E7D60")}
            >
              Crear cuenta
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
