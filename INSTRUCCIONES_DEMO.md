# Instrucciones de demo y despliegue

Este proyecto se compone de:
- `backend/` (FastAPI + SQLite)
- `frontend/` (HTML/CSS/JS estático)

Para una demo pública, despliega **backend** y **frontend** por separado.

---

## 1) Backend (Render / Railway / cualquier host Python)

1. Crear servicio apuntando a la carpeta `backend/`.
2. Configurar comando de instalación:
   - `pip install -r requirements.txt`
3. Configurar comando de inicio:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Variables de entorno mínimas:
   - `SECRET_KEY` = una clave aleatoria segura (64+ caracteres)
   - `DATABASE_URL` = `sqlite:///./gestivoryx.db`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `60`
   - `ALGORITHM` = `HS256`
   - `ALLOWED_ORIGINS` = dominio del frontend (ej: `https://tu-demo.vercel.app`)
5. Verificar backend en:
   - `https://TU_BACKEND_URL/docs`

> Nota: SQLite funciona para demo/MVP. Para producción real, migrar a PostgreSQL.

---

## 2) Frontend en Vercel

1. Importar el repositorio en Vercel.
2. Framework preset: **Other**.
3. Build command: **vacío**.
4. Output directory: **vacío** (sitio estático).
5. Deploy.

La UI quedará disponible en:
- `https://TU_FRONTEND_URL/frontend/login.html`

---

## 3) Conectar frontend con backend (obligatorio para que la demo funcione)

Editar este archivo:
- `frontend/assets/js/api.js`

En la constante `API_BASE`, poner la URL de tu backend desplegado, por ejemplo:
- `https://tu-backend-demo.onrender.com`

Después, volver a desplegar el frontend en Vercel.

---

## 4) Checklist rápido de demo

- [ ] Backend responde en `/docs`
- [ ] Frontend abre `frontend/login.html`
- [ ] Login admin funciona:
  - Usuario: `admin`
  - Contraseña: `admin123`
- [ ] CRUD de productos/categorías/proveedores/clientes operativo
- [ ] Registro de ventas y ajustes operativo

---

## 5) Recomendaciones para presentación de demo

- Cargar 3–5 productos de ejemplo antes de mostrar.
- Crear una venta en vivo para evidenciar descuento de stock.
- Mostrar dashboard al final.
