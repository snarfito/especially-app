/**
 * Especially Frontend — Dashboard del Socio Productor.
 *
 * Lista los pedidos disponibles y asignados al socio.
 * Permite aceptar pedidos y actualizar su estado.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { getCurrentUser, isAuthenticated } from "@/lib/auth";
import type { Order, OrderStatus } from "@/types";

const STATUS_LABELS: Record<OrderStatus, string> = {
  pendiente: "Pendiente",
  aceptado: "Aceptado",
  en_produccion: "En producción",
  enviado: "Enviado",
  entregado: "Entregado",
  cancelado: "Cancelado",
};

const STATUS_COLORS: Record<OrderStatus, string> = {
  pendiente: "bg-yellow-50 text-yellow-700",
  aceptado: "bg-blue-50 text-blue-700",
  en_produccion: "bg-purple-50 text-purple-700",
  enviado: "bg-indigo-50 text-indigo-700",
  entregado: "bg-green-50 text-green-700",
  cancelado: "bg-red-50 text-red-700",
};

export default function DashboardPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    const user = getCurrentUser();
    if (user?.role !== "socio_productor") {
      router.push("/catalogo");
      return;
    }

    api
      .get<Order[]>("/orders/seller/available")
      .then(setOrders)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [router]);

  async function handleAccept(orderId: number) {
    try {
      await api.post(`/orders/${orderId}/accept`, {});
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? { ...o, status: "aceptado" as OrderStatus } : o))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al aceptar pedido");
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <div className="w-8 h-8 border-4 border-jade-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
      <p className="text-gray-500 mb-8">Pedidos disponibles para producción</p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {orders.length === 0 ? (
        <div className="text-center py-24 text-gray-400">No hay pedidos disponibles.</div>
      ) : (
        <div className="flex flex-col gap-4">
          {orders.map((order) => (
            <div
              key={order.id}
              className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-center justify-between"
            >
              <div className="flex flex-col gap-1">
                <span className="font-medium text-gray-900">Pedido #{order.id}</span>
                <span className="text-sm text-gray-500">
                  Total: ${order.total_amount.toLocaleString("es-CO")}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full w-fit font-medium ${STATUS_COLORS[order.status]}`}
                >
                  {STATUS_LABELS[order.status]}
                </span>
              </div>

              {order.status === "pendiente" && (
                <button
                  onClick={() => handleAccept(order.id)}
                  className="bg-jade-500 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-jade-600 transition-colors"
                >
                  Aceptar pedido
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
