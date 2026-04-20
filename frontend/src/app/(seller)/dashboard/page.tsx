/**
 * Especially Frontend — Dashboard del Socio Productor.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { getCurrentUser, isAuthenticated } from "@/lib/auth";
import type { Order } from "@/types";

const JADE = "#2E7D60";
const JADE_DARK = "#1C5241";
const JADE_LIGHT = "#E6F4EE";

const STATUS_LABELS: Record<string, string> = {
  pendiente: "Pendiente",  PENDING: "Pendiente",
  aceptado: "Aceptado",    ACCEPTED: "Aceptado",
  produciendo: "Produciendo", IN_PRODUCTION: "En producción",
  enviado: "Enviado",      SHIPPED: "Enviado",
  entregado: "Entregado",  DELIVERED: "Entregado",
  cancelado: "Cancelado",  CANCELLED: "Cancelado",
};

const STATUS_STYLES: Record<string, { bg: string; color: string }> = {
  pendiente:   { bg: "#FFFBEB", color: "#92400E" },
  PENDING:     { bg: "#FFFBEB", color: "#92400E" },
  aceptado:    { bg: "#EFF6FF", color: "#1E40AF" },
  ACCEPTED:    { bg: "#EFF6FF", color: "#1E40AF" },
  produciendo: { bg: "#F5F3FF", color: "#6B21A8" },
  IN_PRODUCTION:{ bg: "#F5F3FF", color: "#6B21A8" },
  enviado:     { bg: "#F0F9FF", color: "#075985" },
  SHIPPED:     { bg: "#F0F9FF", color: "#075985" },
  entregado:   { bg: JADE_LIGHT, color: JADE_DARK },
  DELIVERED:   { bg: JADE_LIGHT, color: JADE_DARK },
  cancelado:   { bg: "#FEF2F2", color: "#991B1B" },
  CANCELLED:   { bg: "#FEF2F2", color: "#991B1B" },
};

export default function DashboardPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) { router.push("/login"); return; }
    const user = getCurrentUser();
    if (user?.user_role !== "socio_productor" && user?.user_role !== "seller") {
      router.push("/catalogo"); return;
    }
    api.get<Order[]>("/orders/available")
      .then(setOrders)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [router]);

  async function handleAccept(orderId: string) {
    try {
      const updated = await api.post<Order>(`/orders/${orderId}/accept`, {});
      setOrders((prev) => prev.map((o) => (o.order_id === orderId ? updated : o)));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Error al aceptar pedido");
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-32">
        <div
          className="w-7 h-7 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: JADE, borderTopColor: "transparent" }}
        />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-10">
        <h1 className="text-3xl font-bold mb-1" style={{ color: "#0F1F19" }}>
          Dashboard
        </h1>
        <p className="text-sm" style={{ color: "#6B7280" }}>
          Pedidos disponibles para producción
        </p>
      </div>

      {error && (
        <div
          className="text-xs rounded-xl px-4 py-3 mb-6"
          style={{ backgroundColor: "#FEF2F2", color: "#DC2626", border: "1px solid #FCA5A5" }}
        >
          {error}
        </div>
      )}

      {orders.length === 0 ? (
        <div className="text-center py-32 text-sm" style={{ color: "#9CA3AF" }}>
          No hay pedidos disponibles en este momento.
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {orders.map((order) => {
            const statusStyle = STATUS_STYLES[order.status] ?? { bg: "#F3F4F6", color: "#374151" };
            const isPending = order.status === "PENDING" || order.status === "pendiente";
            return (
              <div
                key={order.order_id}
                className="bg-white rounded-2xl px-6 py-5 flex items-center justify-between"
                style={{ border: "1px solid #E5E7EB" }}
              >
                <div className="flex flex-col gap-1.5">
                  <span className="text-sm font-semibold" style={{ color: "#111827" }}>
                    Pedido #{order.order_id.slice(0, 8).toUpperCase()}
                  </span>
                  <span className="text-xs" style={{ color: "#9CA3AF" }}>
                    Total: ${Number(order.total_amount).toLocaleString("es-CO")}
                  </span>
                  <span
                    className="text-xs px-2.5 py-0.5 rounded-full font-medium w-fit"
                    style={{ backgroundColor: statusStyle.bg, color: statusStyle.color }}
                  >
                    {STATUS_LABELS[order.status] ?? order.status}
                  </span>
                </div>

                {isPending && (
                  <button
                    onClick={() => handleAccept(order.order_id)}
                    className="text-sm text-white px-5 py-2 rounded-full font-medium transition-colors"
                    style={{ backgroundColor: JADE }}
                    onMouseEnter={e => (e.currentTarget.style.backgroundColor = JADE_DARK)}
                    onMouseLeave={e => (e.currentTarget.style.backgroundColor = JADE)}
                  >
                    Aceptar
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
