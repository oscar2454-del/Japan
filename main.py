from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from mysql.connector import pooling, Error
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="API de Telemetría Dyno")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "RipHawai"),
    "database": os.getenv("DB_NAME", "dyno"),
    "port": int(os.getenv("DB_PORT", 3306))
}

try:
    pool = pooling.MySQLConnectionPool(
        pool_name="dynopool",
        pool_size=5,
        **db_config
    )
    print("Pool de conexiones creado con éxito.")
except Error as e:
    print(f"Error al crear el pool de conexiones: {e}")
    pool = None

# --- 3. RUTAS ---

@app.get("/", response_class=HTMLResponse)
async def home():
    """Sirve la interfaz principal."""
    path = "templates/base.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: Archivo base.html no encontrado en /templates</h1>"

@app.get("/telemetria")
def obtener_telemetria():
    if not pool:
        raise HTTPException(status_code=500, detail="Base de datos no disponible")

    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM telemetria ORDER BY id DESC LIMIT 50"
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        return resultados

    except Error as e:
        print(f"Error en la consulta: {e}")
        raise HTTPException(status_code=500, detail="Error interno al consultar la base de datos")

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
