/**
 * Especially Frontend — Página de inicio.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center gap-6">
      <h1 className="text-5xl font-bold text-gray-900">
        Personaliza lo que <span className="text-jade-600">usas</span>
      </h1>
      <p className="text-lg text-gray-500 max-w-xl">
        Crea productos únicos con tus diseños o descubre artesanías auténticas colombianas.
      </p>
      <div className="flex gap-4 mt-4">
        <Link
          href="/catalogo"
          className="bg-jade-500 text-white px-6 py-3 rounded-full font-medium hover:bg-jade-600 transition-colors"
        >
          Ver catálogo
        </Link>
        <Link
          href="/registro"
          className="border border-gray-300 text-gray-700 px-6 py-3 rounded-full font-medium hover:border-jade-500 hover:text-jade-600 transition-colors"
        >
          Crear cuenta
        </Link>
      </div>
    </div>
  );
}
