import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard de Sentencias", layout="wide", page_icon="⚖️")
st.title("⚖️ Reporte de Sentencias de Vista y Jurisprudencia")
st.markdown("---")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("datos.xlsx")
    df = df.fillna("")
    return df

@st.cache_data
def cargar_textos():
    try:
        return pd.read_csv("textos_jurisprudencia.csv")
    except:
        return pd.DataFrame()

datos = cargar_datos()
textos = cargar_textos()

# === CREACIÓN DE LAS PESTAÑAS ===
tab1, tab2 = st.tabs(["📊 Indicadores Estadísticos", "🔍 Buscador de Jurisprudencia"])

# --- PESTAÑA 1: ESTADÍSTICAS ---
with tab1:
    columna_ano = next((col for col in datos.columns if 'AÑO' in col.upper() or 'ANO' in col.upper()), None)
    if columna_ano:
        anos_disponibles = sorted(list(datos[columna_ano].dropna().unique()))
        anos_disponibles.insert(0, 'Todos los años')
        ano_seleccionado = st.selectbox("📅 Filtrar información por Año:", anos_disponibles)
        if ano_seleccionado != 'Todos los años':
            datos_filtrados = datos[datos[columna_ano] == ano_seleccionado]
        else:
            datos_filtrados = datos
    else:
        datos_filtrados = datos

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Expedientes", len(datos_filtrados))
    
    col_est = next((col for col in datos.columns if 'ESTADO' in col.upper()), None)
    if col_est:
        col2.metric("Confirmadas", len(datos_filtrados[datos_filtrados[col_est].astype(str).str.contains('CONFIRMA', case=False, na=False)]))
        col3.metric("Revocadas", len(datos_filtrados[datos_filtrados[col_est].astype(str).str.contains('REVOCA', case=False, na=False)]))
    
    col_cas = next((col for col in datos.columns if 'CASACION' in col.upper()), None)
    if col_cas:
        col4.metric("Casaciones", len(datos_filtrados[datos_filtrados[col_cas].astype(str).str.contains('SI', case=False, na=False)]))

    st.write("### Detalle de Expedientes")
    st.dataframe(datos_filtrados, use_container_width=True)

# --- PESTAÑA 2: BUSCADOR ---
with tab2:
    st.subheader("Búsqueda en Resoluciones de Vista")
    palabra_clave = st.text_input("Ingrese la palabra clave (ej. 'Lavado de Activos', 'Casación N°'):", "")
    
    if palabra_clave:
        if not textos.empty:
            resultados = textos[textos['TEXTO_JURISPRUDENCIA'].str.contains(palabra_clave, case=False, na=False)]
            st.success(f"Se encontraron {len(resultados)} resoluciones que contienen: '{palabra_clave}'")
            
            if not resultados.empty:
                # Mostramos solo el nombre del archivo para que la tabla sea fácil de leer
                st.dataframe(resultados[['NOMBRE_ARCHIVO']], use_container_width=True)
        else:
            st.warning("El archivo de jurisprudencia aún no está disponible.")
