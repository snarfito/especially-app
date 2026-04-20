#!/bin/bash
cd /Users/fredyhortua/Personal/Proyectos/Especially/especially-app

echo "📦 Agregando archivos..."
git add -A

echo "📝 Haciendo commit..."
git commit -m "fix: conectar frontend al backend real (puerto 8001, OAuth2, tipos alineados)

- .env.local: puerto 8000 → 8001
- CORS backend: localhost:3001, 127.0.0.1:3000/3001
- auth.ts: login via /token (OAuth2 form-urlencoded) + /users/me
- types/index.ts: alinear user_id, user_role, product_id, images[], order_id
- login page: user_role buyer/seller, redirección correcta
- registro page: user_role buyer/seller, botones actualizados
- catalogo: product_id, images[0].url, Number() para Decimal
- dashboard: /orders/available, order_id, status bilingue PENDING/pendiente"

echo "🚀 Haciendo push..."
git push

echo ""
echo "✅ ¡Listo! Commit y push completados."
