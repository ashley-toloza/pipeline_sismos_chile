import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard de Sismos Chile 2026", layout="wide")

st.title("🌋 Dashboard Analítico de Sismología en Chile")
st.markdown("Solución conectada al repositorio analítico **SQLite** construida desde la canalización ETL.")

db_path = os.path.join("data", "processed", "sismos_analitico.db")

@st.cache_data
def cargar_datos(query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if os.path.exists(db_path):
    df_sismos = cargar_datos("SELECT * FROM sismos")
    df_resumen_mes = cargar_datos("SELECT * FROM vista_resumen_mensual")
    df_resumen_reg = cargar_datos("SELECT * FROM vista_resumen_regional")

    st.sidebar.header("Filtros de Análisis")
    
    min_mag = float(df_sismos['magnitude'].min())
    max_mag = float(df_sismos['magnitude'].max())
    rango_magnitud = st.sidebar.slider(
        "Rango de Magnitud (Richter):",
        min_value=min_mag,
        max_value=max_mag,
        value=(min_mag, max_mag),
        step=0.1
    )

    regiones_disponibles = ["Todas"] + list(df_sismos['region'].unique())
    region_sel = st.sidebar.selectbox("Filtrar por Región:", regiones_disponibles)

    # Filtrado dinámico
    df_filtrado = df_sismos[
        (df_sismos['magnitude'] >= rango_magnitud[0]) & 
        (df_sismos['magnitude'] <= rango_magnitud[1])
    ]
    if region_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['region'] == region_sel]

    # Indicadores Clave
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sismos", len(df_filtrado))
    col2.metric("Magnitud Promedio", f"{df_filtrado['magnitude'].mean():.2f}" if len(df_filtrado) > 0 else "0")
    col3.metric("Magnitud Máxima", f"{df_filtrado['magnitude'].max():.1f}" if len(df_filtrado) > 0 else "0")
    col4.metric("Profundidad Promedio", f"{df_filtrado['depth'].mean():.1f} km" if len(df_filtrado) > 0 else "0")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["🗺️ Mapa Geográfico", "🏛️ Distribución por Región", "📈 Tendencias Temporales"])

    with tab1:
        st.subheader("Ubicación Geográfica y Magnitud")
        fig_mapa = px.scatter_map(
            df_filtrado,
            lat="latitude",
            lon="longitude",
            size="magnitude",
            color="magnitude",
            color_continuous_scale=px.colors.sequential.OrRd,
            zoom=3.5,
            center={"lat": -35.6751, "lon": -71.5430},
            hover_data=["datetime", "region", "depth", "magnitude"],
            height=600
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

    with tab2:
        st.subheader("Concentración de Sismos por Región (Vista SQL)")
        fig_region = px.bar(
            df_resumen_reg,
            x="total_sismos",
            y="region",
            orientation="h",
            color="total_sismos",
            color_continuous_scale=px.colors.sequential.Reds,
            title="Total de Eventos Registrados por Zonas/Regiones",
            labels={"total_sismos": "Frecuencia de Sismos", "region": "Región / Zona"}
        )
        fig_region.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_region, use_container_width=True)

    with tab3:
        st.subheader("Evolución Temporal Consolidada")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_linea = px.line(
                df_resumen_mes,
                x="mes",
                y="total_sismos",
                markers=True,
                title="Cantidad Total de Sismos por Mes",
                labels={"mes": "Mes", "total_sismos": "Frecuencia"}
            )
            st.plotly_chart(fig_linea, use_container_width=True)

        with col_g2:
            fig_barras = px.bar(
                df_resumen_mes,
                x="mes",
                y="magnitud_promedio",
                title="Magnitud Promedio por Mes",
                labels={"mes": "Mes", "magnitud_promedio": "Magnitud Promedio"}
            )
            st.plotly_chart(fig_barras, use_container_width=True)

else:
    st.error("No se ha encontrado la base de datos analítica. Ejecuta primero `python src/etl.py`.")