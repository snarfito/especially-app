/**
 * Especially Frontend — Tipos TypeScript globales.
 *
 * Refleja los modelos del backend FastAPI.
 * Fuente de verdad para todos los tipos usados en el frontend.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

// ─── Auth ────────────────────────────────────────────────────────────────────

export type UserRole = "comprador" | "socio_productor" | "disenador";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ─── Productos ───────────────────────────────────────────────────────────────

export interface Product {
  id: number;
  name: string;
  description: string;
  base_price: number;
  image_url: string | null;
  is_customizable: boolean;
  store_id: number;
  is_active: boolean;
}

export interface ProductCreate {
  name: string;
  description: string;
  base_price: number;
  is_customizable: boolean;
}

// ─── Tiendas ─────────────────────────────────────────────────────────────────

export interface Store {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  is_active: boolean;
}

// ─── Pedidos ─────────────────────────────────────────────────────────────────

export type OrderStatus =
  | "pendiente"
  | "aceptado"
  | "en_produccion"
  | "enviado"
  | "entregado"
  | "cancelado";

export interface OrderItem {
  product_id: number;
  quantity: number;
  unit_price: number;
  custom_design_url?: string;
}

export interface Order {
  id: number;
  buyer_id: number;
  status: OrderStatus;
  total_amount: number;
  items: OrderItem[];
  created_at: string;
}

// ─── API Genérico ─────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
