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

/** Roles del backend: buyer = comprador, seller = socio_productor */
export type UserRole = "buyer" | "seller" | "comprador" | "socio_productor" | "disenador";

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  user_role: string;
}

/** Refleja el schema User del backend */
export interface User {
  user_id: string;
  email: string;
  full_name: string;
  user_role: string;
  city?: string | null;
}

/** El backend /token devuelve solo el token; el user viene de /users/me */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/** Tipo compuesto que usamos internamente en el frontend */
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ─── Productos ───────────────────────────────────────────────────────────────

export interface ProductImage {
  image_id: string;
  url: string;
  view_type: string;
  display_order: number;
}

export interface StoreProfile {
  store_id: string;
  brand_name: string;
  bio?: string | null;
  logo_url?: string | null;
}

export interface Product {
  product_id: string;
  name: string;
  description?: string | null;
  category: string;
  base_price: number;
  is_customizable: boolean;
  stock_quantity: number;
  images: ProductImage[];
  store?: StoreProfile | null;
  created_at?: string | null;
}

export interface ProductCreate {
  name: string;
  description?: string;
  category: string;
  base_price: number;
  is_customizable: boolean;
  stock_quantity?: number;
}

// ─── Tiendas ─────────────────────────────────────────────────────────────────

export interface Store {
  store_id: string;
  brand_name: string;
  bio?: string | null;
  is_business: boolean;
  logo_url?: string | null;
}

// ─── Pedidos ─────────────────────────────────────────────────────────────────

export type OrderStatus =
  | "PENDING"
  | "ACCEPTED"
  | "IN_PRODUCTION"
  | "SHIPPED"
  | "DELIVERED"
  | "CANCELLED"
  // aliases en español (por si el backend los devuelve en minúscula)
  | "pendiente"
  | "aceptado"
  | "en_produccion"
  | "enviado"
  | "entregado"
  | "cancelado";

export interface OrderItem {
  item_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  size?: string | null;
  garment_color?: string | null;
}

export interface Order {
  order_id: string;
  status: OrderStatus;
  total_amount: number;
  shipping_address: string;
  items: OrderItem[];
  created_at?: string | null;
  payment_status?: string;
  spec_pdf_url?: string | null;
}

// ─── API Genérico ─────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
