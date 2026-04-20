/**
 * Especially Frontend — Página de Catálogo.
 *
 * Lista todos los productos activos del marketplace.
 * Permite filtrar por nombre y tipo (personalizables / artesanías).
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Product } from "@/types";

export default function CatalogoPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .get<Product[]>("/products")
      .then(setProducts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <div className="w-8 h-8 border-4 border-jade-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-24 text-red-500">
        Error cargando productos: {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Catálogo</h1>
      <p className="text-gray-500 mb-8">Productos personalizables y artesanías auténticas</p>

      {products.length === 0 ? (
        <div className="text-center py-24 text-gray-400">
          Aún no hay productos disponibles.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <div
              key={product.product_id}
              className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="bg-gray-100 h-48 flex items-center justify-center text-gray-300 text-sm">
                {product.images?.[0]?.url ? (
                  <img
                    src={product.images[0].url}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span>Sin imagen</span>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-medium text-gray-900 text-sm truncate">{product.name}</h3>
                <p className="text-jade-600 font-bold mt-1">
                  ${Number(product.base_price).toLocaleString("es-CO")}
                </p>
                {product.is_customizable && (
                  <span className="inline-block mt-2 text-xs bg-jade-50 text-jade-700 px-2 py-0.5 rounded-full">
                    Personalizable
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
