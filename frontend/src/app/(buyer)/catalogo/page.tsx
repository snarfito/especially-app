/**
 * Especially Frontend — Catálogo de productos.
 */

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Product } from "@/types";

export default function CatalogoPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Product[]>("/products")
      .then(setProducts)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-32">
        <div
          className="w-7 h-7 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: "#2E7D60", borderTopColor: "transparent" }}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-32 text-sm" style={{ color: "#DC2626" }}>
        Error cargando productos: {error}
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-1" style={{ color: "#0F1F19" }}>
          Catálogo
        </h1>
        <p className="text-sm" style={{ color: "#6B7280" }}>
          Productos personalizables y artesanías auténticas colombianas
        </p>
      </div>

      {products.length === 0 ? (
        <div className="text-center py-32 text-sm" style={{ color: "#9CA3AF" }}>
          Aún no hay productos disponibles.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {products.map((product) => (
            <div
              key={product.product_id}
              className="group bg-white rounded-2xl overflow-hidden cursor-pointer transition-shadow hover:shadow-md"
              style={{ border: "1px solid #E5E7EB" }}
            >
              {/* Imagen */}
              <div
                className="h-52 flex items-center justify-center overflow-hidden"
                style={{ backgroundColor: "#F9FAFB" }}
              >
                {product.images?.[0]?.url ? (
                  <img
                    src={product.images[0].url}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <span className="text-xs" style={{ color: "#D1D5DB" }}>
                    Sin imagen
                  </span>
                )}
              </div>

              {/* Info */}
              <div className="p-4">
                {/* Tienda */}
                {product.store && (
                  <p className="text-xs mb-1 truncate" style={{ color: "#9CA3AF" }}>
                    {product.store.brand_name}
                  </p>
                )}
                <h3 className="text-sm font-semibold truncate mb-2" style={{ color: "#111827" }}>
                  {product.name}
                </h3>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold" style={{ color: "#2E7D60" }}>
                    ${Number(product.base_price).toLocaleString("es-CO")}
                  </span>
                  {product.is_customizable && (
                    <span
                      className="text-xs px-2 py-0.5 rounded-full font-medium"
                      style={{ backgroundColor: "#E6F4EE", color: "#1C5241" }}
                    >
                      Personalizable
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
