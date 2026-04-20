/**
 * Especially Frontend — Layout raíz.
 *
 * Envuelve toda la aplicación. Incluye Navbar y fuentes globales.
 *
 * Desarrollador: Fredy Hortua <fredy.hortua@gmail.com>
 * Proyecto:      Especially — Marketplace colombiano de personalización y artesanías
 */

import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

const geist = Geist({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Especially — Personaliza lo que usas",
  description: "Marketplace colombiano de productos personalizados y artesanías auténticas.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={`${geist.className} min-h-screen`} style={{ backgroundColor: '#FAF8F4', color: '#0F1F19' }}>
        <Navbar />
        <main className="max-w-7xl mx-auto px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
