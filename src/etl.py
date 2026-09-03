import pandas as pd
import sqlite3
import os

def asignar_region(lat):
    if lat >= -18.5: return "Arica y Parinacota"
    elif lat >= -21.5: return "Tarapacá"
    elif lat >= -26.0: return "Antofagasta"
    elif lat >= -29.0: return "Atacama"
    elif lat >= -32.2: return "Coquimbo"
    elif lat >= -33.9: return "Valparaíso / RM"
    elif lat >= -35.0: return "O'Higgins"
    elif lat >= -36.5: return "Maule"
    elif lat >= -38.5: return "Ñuble / Bío Bío"
    elif lat >= -40.5: return "Araucanía / Los Ríos"
    elif lat >= -44.0: return "Los Lagos"
    elif lat >= -48.0: return "Aysén"
    else: return "Magallanes y Antártica"

def ejecutar_etl():
    print("1. Extrayendo datos desde el CSV...")
    raw_path = os.path.join("data", "raw", "earthquakes_chile.csv")
    
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No se encontró el archivo {raw_path}.")

    df_raw = pd.read_csv(raw_path)

    print("2. Estandarizando y enriqueciendo variables...")
    renombres = {
        'Date(UTC)': 'datetime',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Depth': 'depth',
        'Magnitude': 'magnitude'
    }
    df_clean = df_raw.rename(columns=renombres).copy()

    # Limpieza de nulos
    columnas_clave = ['latitude', 'longitude', 'magnitude', 'depth', 'datetime']
    df_clean = df_clean.dropna(subset=columnas_clave)

    # Conversión temporal
    df_clean['datetime'] = pd.to_datetime(df_clean['datetime'])

    # Simulación a 2026
    max_year = df_clean['datetime'].dt.year.max()
    desfase_anos = 2026 - max_year
    df_clean['datetime'] = df_clean['datetime'] + pd.DateOffset(years=desfase_anos)

    # Métricas y dimensiones derivadas (Ingeniería de Características)
    df_clean['año'] = df_clean['datetime'].dt.year
    df_clean['mes'] = df_clean['datetime'].dt.month
    df_clean['fecha_corta'] = df_clean['datetime'].dt.strftime('%Y-%m-%d')
    df_clean['region'] = df_clean['latitude'].apply(asignar_region)

    print("3. Cargando datos en el Repositorio Analítico (SQLite)...")
    os.makedirs(os.path.join("data", "processed"), exist_ok=True)
    db_path = os.path.join("data", "processed", "sismos_analitico.db")
    
    conn = sqlite3.connect(db_path)
    
    # Tabla principal
    df_clean.to_sql("sismos", conn, if_exists="replace", index=False)

    # Vista 1: Resumen mensual
    conn.execute("""
    CREATE VIEW IF NOT EXISTS vista_resumen_mensual AS
    SELECT 
        año,
        mes,
        COUNT(*) AS total_sismos,
        ROUND(AVG(magnitude), 2) AS magnitud_promedio,
        MAX(magnitude) AS magnitud_maxima,
        ROUND(AVG(depth), 2) AS profundidad_promedio
    FROM sismos
    GROUP BY año, mes;
    """)

    # Vista 2: Resumen por región
    conn.execute("""
    CREATE VIEW IF NOT EXISTS vista_resumen_regional AS
    SELECT 
        region,
        COUNT(*) AS total_sismos,
        ROUND(AVG(magnitude), 2) AS magnitud_promedio,
        MAX(magnitude) AS magnitud_maxima
    FROM sismos
    GROUP BY region
    ORDER BY total_sismos DESC;
    """)

    conn.commit()
    conn.close()
    
    print("¡ETL completado exitosamente con enriquecimiento regional!")

if __name__ == "__main__":
    ejecutar_etl()