from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="API de Telemetría Dyno")

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "RipHawai",
    "database": "Dyno"
}

def db ():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home():
    path = "templates/base.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Archivo base.html no encontrado en la carpeta templates</h1>"

@app.get("/telemetria")
def obtener_telemetria():
    conn = db()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM telemetria")
    resultados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return resultados