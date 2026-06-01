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
                # 1. Preparamos la tabla básica con los nombres encontrados
                df_mostrar = resultados[['NOMBRE_ARCHIVO']].copy()
                
                # 2. Cruzamos la información con tu Excel para traer los enlaces de Drive
                if 'NOMBRE_ARCHIVO' in datos.columns and 'ENLACE_PDF' in datos.columns:
                    # Une el Excel con los resultados usando el nombre del archivo como puente
                    df_mostrar = pd.merge(df_mostrar, datos[['NOMBRE_ARCHIVO', 'ENLACE_PDF']], on='NOMBRE_ARCHIVO', how='left')
                else:
                    # Si aún no configuras el Excel, te avisa
                    df_mostrar['ENLACE_PDF'] = "Faltan columnas en Excel"
                
                # 3. Mostramos la tabla con enlaces clickeables
                st.dataframe(
                    df_mostrar,
                    column_config={
                        "NOMBRE_ARCHIVO": "Nombre del Documento",
                        "ENLACE_PDF": st.column_config.LinkColumn(
                            "🔗 Enlace al Expediente", 
                            display_text="Abrir PDF en Drive" # Esto oculta la URL larga y pone un texto limpio
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.warning("El archivo de jurisprudencia aún no está disponible.")
