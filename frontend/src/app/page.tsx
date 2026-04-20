/**
 * Especially Frontend — Página de inicio.
 */

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center py-32 text-center gap-8">
      <div className="flex flex-col items-center gap-4">
        <span
          className="text-xs font-semibold tracking-widest uppercase px-3 py-1 rounded-full"
          style={{ backgroundColor: "#E6F4EE", color: "#1C5241" }}
        >
          Marketplace colombiano
        </span>
        <h1 className="text-5xl font-bold leading-tight" style={{ color: "#0F1F19" }}>
          Personaliza lo que{" "}
          <span style={{ color: "#2E7D60" }}>usas</span>
        </h1>
        <p className="text-lg max-w-lg leading-relaxed" style={{ color: "#6B7280" }}>
          Crea productos únicos con tus diseños o descubre artesanías
          auténticas colombianas.
        </p>
      </div>

      <div className="flex gap-3 mt-2">
        <Link
          href="/catalogo"
          className="px-6 py-3 rounded-full font-semibold text-sm text-white transition-colors"
          style={{ backgroundColor: "#2E7D60" }}
        >
          Ver catálogo
        </Link>
        <Link
          href="/registro"
          className="px-6 py-3 rounded-full font-semibold text-sm border border-gray-300 transition-colors"
          style={{ color: "#374151" }}
        >
          Crear cuenta
        </Link>
      </div>
    </div>
  );
}
