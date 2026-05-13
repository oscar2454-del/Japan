from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import pooling, Error
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="API de Telemetría Dyno")

db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "RipHawai"),
    "database": os.getenv("DB_NAME", "dyno"),
    "port": 3306
}

try:
    pool = pooling.MySQLConnectionPool(
        pool_name="dynopool",
        pool_size=5,
        **db_config
    )
except Error as e:
    print(f"Error al crear el pool de conexiones: {e}")
    pool = None

# --- Rutas ---

@app.get("/", response_class=HTMLResponse)
async def home():
    path = "templates/base.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: Archivo base.html no encontrado</h1>"

@app.get("/telemetria")
def obtener_telemetria():
    if not pool:
        raise HTTPException(status_code=500, detail="Base de datos no configurada")

    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM telemetria ORDER BY id DESC LIMIT 50")
        resultados = cursor.fetchall()
        
        return resultados

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta: {e}")

    finally:
        # Aquí no cerramos la conexión, la devolvemos al pool para el siguiente
        if conn and conn.is_connected():
            cursor.close()
            conn.close()