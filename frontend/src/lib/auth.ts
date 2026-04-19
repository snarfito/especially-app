/**
 * Especially Frontend — Utilidades de autenticación.
 *
 * Maneja almacenamiento y lectura del JWT.
 * Provee helpers para login, logout y verificar sesión activa.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

import { api } from "./api";
import type { AuthResponse, LoginCredentials, User } from "@/types";

/**
 * Inicia sesión contra el backend y almacena el token.
 *
 * Args:
 *   credentials: Email y password del usuario.
 *
 * Returns:
 *   El objeto AuthResponse con access_token y datos del usuario.
 */
export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const data = await api.post<AuthResponse>("/auth/login", credentials);
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
}

/**
 * Cierra la sesión eliminando el token y datos del usuario.
 */
export function logout(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
}

/**
 * Retorna el usuario autenticado desde localStorage.
 *
 * Returns:
 *   El objeto User o null si no hay sesión activa.
 */
export function getCurrentUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

/**
 * Verifica si hay una sesión activa.
 *
 * Returns:
 *   true si existe un token almacenado.
 */
export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}
