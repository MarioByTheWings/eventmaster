# 🎟️ EventMaster API

API REST para gestión de recintos y eventos con control de aforo.
Construida con **FastAPI** + **SQLAlchemy** + **PostgreSQL (Aiven)** y desplegada en **Railway**.

---

## 📋 Índice

1. [Configuración de la base de datos en Aiven](#1-configuración-de-la-base-de-datos-en-aiven)
2. [Despliegue en Railway](#2-despliegue-en-railway)
3. [Ejecución local](#3-ejecución-local)
4. [Prueba de los endpoints](#4-prueba-de-los-endpoints)

---

## 1. Configuración de la base de datos en Aiven

1. Ve a [aiven.io](https://aiven.io) e inicia sesión o crea una cuenta gratuita.
2. Crea un nuevo servicio → **PostgreSQL** → elige el plan *Free* y la región más cercana.
3. Espera a que el servicio pase a estado **Running** (puede tardar 1-2 minutos).
4. En la pestaña **Overview** de tu servicio, copia la **Service URI**, que tiene este formato:
   ```
   postgresql://avnadmin:PASSWORD@HOST:PORT/defaultdb?sslmode=require
   ```
5. Guarda esa URI, la necesitarás en los pasos siguientes.

---

## 2. Despliegue en Railway

### 2.1 Preparar el repositorio

1. Asegúrate de que el proyecto está subido a **GitHub** (el `.env` debe estar en `.gitignore` y **NO** subirse).
2. El repositorio debe contener el archivo `requirements.txt` con todas las dependencias.

### 2.2 Crear el proyecto en Railway

1. Ve a [railway.app](https://railway.app) e inicia sesión con tu cuenta de GitHub.
2. Pulsa **New Project** → **Deploy from GitHub repo** → selecciona tu repositorio.
3. Railway detectará automáticamente que es una app Python.

### 2.3 Añadir la variable de entorno

1. En tu proyecto de Railway, ve a la pestaña **Variables**.
2. Pulsa **New Variable** y añade:
   - **Name:** `DATABASE_URL`
   - **Value:** la URI de Aiven que copiaste antes.
3. Railway redesplegará la aplicación automáticamente.

### 2.4 Verificar el despliegue

1. Ve a la pestaña **Settings** → **Domains** y copia la URL pública asignada (ej: `https://eventmaster-xxx.up.railway.app`).
2. Abre esa URL en el navegador. Deberías ver:
   ```json
   {"message": "Bienvenido a la API de EventMaster", "documentacion": "/docs"}
   ```
3. La documentación interactiva estará disponible en `<TU_URL>/docs`.

---

## 3. Ejecución local

### 3.1 Configurar el entorno

1. Copia el archivo de ejemplo y rellena tu `DATABASE_URL`:
   ```bash
   cp .env.example .env
   # Edita .env y añade tu DATABASE_URL de Aiven
   ```
2. Si no tienes PostgreSQL disponible localmente, puedes dejarlo sin `DATABASE_URL` y la app usará **SQLite** automáticamente para desarrollo.

### 3.2 Instalar dependencias y arrancar

```bash
# Con uv (recomendado)
uv run uvicorn main:app --reload

# Con pip tradicional
pip install -r requirements.txt
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

---

## 4. Prueba de los endpoints

Puedes probar la API desde la **UI de Swagger** en `/docs`, o con los siguientes comandos `curl`:

### 🏟️ Recintos

**Crear un recinto:**
```bash
curl -X POST http://127.0.0.1:8000/recintos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Wizink Center", "ciudad": "Madrid", "capacidad": 100}'
```

**Listar todos los recintos:**
```bash
curl http://127.0.0.1:8000/recintos/
```

**Actualizar un recinto (id=1):**
```bash
curl -X PUT http://127.0.0.1:8000/recintos/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Wizink Center", "ciudad": "Madrid", "capacidad": 200}'
```

**Eliminar un recinto (id=1):**
```bash
curl -X DELETE http://127.0.0.1:8000/recintos/1
```

---

### 🎭 Eventos

**Crear un evento (recinto_id debe existir):**
```bash
curl -X POST http://127.0.0.1:8000/eventos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Concierto de Rock", "fecha": "2026-06-15T20:00:00", "precio": 45.50, "recinto_id": 1}'
```

**Listar todos los eventos:**
```bash
curl http://127.0.0.1:8000/eventos/
```

**Filtrar eventos por ciudad:**
```bash
curl "http://127.0.0.1:8000/eventos/?ciudad=Madrid"
```

---

### 🎟️ Compra de tickets

**Comprar tickets (id evento=1, cantidad=10):**
```bash
curl -X PATCH http://127.0.0.1:8000/eventos/1/comprar \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 10}'
```

**Probar error de aforo** (pide más tickets de los disponibles):
```bash
curl -X PATCH http://127.0.0.1:8000/eventos/1/comprar \
  -H "Content-Type: application/json" \
  -d '{"cantidad": 99999}'
```
Respuesta esperada:
```json
{"detail": "Aforo insuficiente en el recinto"}
```

**Probar error de precio negativo** (al crear evento):
```bash
curl -X POST http://127.0.0.1:8000/eventos/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Test", "fecha": "2026-01-01T00:00:00", "precio": -5, "recinto_id": 1}'
```
Respuesta esperada: error `422 Unprocessable Entity`.

---

## 🗂️ Estructura del proyecto

```
Boletín 7/
├── main.py           # Endpoints de la API
├── models.py         # Modelos SQLAlchemy y esquemas Pydantic
├── requirements.txt  # Dependencias
├── .env              # Variables de entorno locales (NO subir a Git)
├── .env.example      # Plantilla de variables de entorno
└── .gitignore
```
