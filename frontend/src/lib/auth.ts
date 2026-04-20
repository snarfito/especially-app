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
import type { AuthResponse, TokenResponse, User } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

/**
 * Inicia sesión contra el backend usando el flujo OAuth2 password.
 * El backend espera application/x-www-form-urlencoded en /token.
 * Luego obtiene el perfil del usuario desde /users/me.
 */
export async function login(credentials: { email: string; password: string }): Promise<AuthResponse> {
  // El endpoint /token usa OAuth2PasswordRequestForm → form-urlencoded
  const formBody = new URLSearchParams({
    username: credentials.email,
    password: credentials.password,
  });

  const response = await fetch(`${API_URL}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formBody.toString(),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Error de autenticación" }));
    throw new Error(err.detail ?? `HTTP ${response.status}`);
  }

  const tokenData = (await response.json()) as TokenResponse;
  localStorage.setItem("access_token", tokenData.access_token);

  // Obtener perfil del usuario
  const user = await api.get<User>("/users/me");
  localStorage.setItem("user", JSON.stringify(user));

  return { ...tokenData, user };
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
 */
export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}
