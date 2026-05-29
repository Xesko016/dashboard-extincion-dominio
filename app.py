import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica de la página
st.set_page_config(page_title="Dashboard de Sentencias", layout="wide", page_icon="⚖️")

st.title("⚖️ Reporte de Sentencias de Vista")
st.subheader("Unidad Especializada en Extinción de Dominio")
st.markdown("---")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("datos.xlsx")
    df = df.fillna("")
    for col in df.columns:
        if 'FECHA' in col.upper():
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y')
            except:
                pass
    return df

try:
    # 1. CARGA DE DATOS MAESTRA
    datos_completos = cargar_datos()
    
    # === NUEVO: FILTRO GLOBAL POR AÑO ===
    # Busca la columna AÑO o ANO para evitar problemas con la Ñ
    columna_ano = next((col for col in datos_completos.columns if 'AÑO' in col.upper() or 'ANO' in col.upper()), None)
    
    if columna_ano:
        # Extraer los años únicos, quitar vacíos y ordenarlos
        anos_disponibles = sorted(list(datos_completos[columna_ano].dropna().unique()))
        anos_disponibles.insert(0, 'Todos los años') # Opción por defecto
        
        ano_seleccionado = st.selectbox("📅 Filtrar información por Año:", anos_disponibles)
        
        # Aplicar el filtro a los datos
        if ano_seleccionado != 'Todos los años':
            datos = datos_completos[datos_completos[columna_ano] == ano_seleccionado]
        else:
            datos = datos_completos
    else:
        datos = datos_completos
        st.warning("No se encontró una columna llamada 'AÑO' para habilitar el filtro temporal.")
        
    st.markdown("---")

    # === SECCIÓN 1: MÉTRICAS PRINCIPALES ===
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total de Expedientes", len(datos))
    
    # Búsqueda flexible de columnas para evitar errores feos
    columna_estado = next((col for col in datos.columns if 'ESTADO' in col.upper()), None)
    if columna_estado:
        confirmadas = len(datos[datos[columna_estado].astype(str).str.contains('CONFIRMA', na=False, case=False)])
        revocadas = len(datos[datos[columna_estado].astype(str).str.contains('REVOCA', na=False, case=False)])
        col2.metric("Sentencias Confirmadas", confirmadas)
        col3.metric("Sentencias Revocadas", revocadas)
    else:
        col2.metric("Confirmadas", "-")
        col3.metric("Revocadas", "-")
        
    columna_casacion = next((col for col in datos.columns if 'CASACION' in col.upper()), None)
    if columna_casacion:
        casaciones = len(datos[datos[columna_casacion].astype(str).str.contains('SI', na=False, case=False)])
        col4.metric("Recursos de Casación", casaciones)
    else:
        col4.metric("Casaciones", "-")

    st.markdown("---")

    # === SECCIÓN 2: GRÁFICOS INTERACTIVOS ===
    graf_col1, graf_col2 = st.columns(2)
    
    with graf_col1:
        st.write("### Distribución por Sala")
        if 'SALA' in datos.columns:
            conteo_salas = datos['SALA'].value_counts().reset_index()
            conteo_salas.columns = ['Sala', 'Cantidad']
            fig_salas = px.pie(conteo_salas, values='Cantidad', names='Sala', hole=0.4, 
                               color_discrete_sequence=px.colors.sequential.Blues_r)
            
            # NUEVO: Forzar que se muestre la cantidad exacta al pasar el mouse
            fig_salas.update_traces(hovertemplate='<b>Sala: %{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}')
            
            st.plotly_chart(fig_salas, use_container_width=True)
        else:
            st.info("Gráfico no disponible: Falta columna 'SALA' en el Excel.")

    with graf_col2:
        st.write("### Carga por Mes")
        if 'MES' in datos.columns:
            meses_orden = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
                           'JULIO', 'AGOSTO', 'SETIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
            datos['MES'] = pd.Categorical(datos['MES'].astype(str).str.upper(), categories=meses_orden, ordered=True)
            
            conteo_mes = datos['MES'].value_counts().sort_index().reset_index()
            conteo_mes.columns = ['Mes', 'Cantidad']
            
            fig_mes = px.bar(conteo_mes, x='Mes', y='Cantidad', color_discrete_sequence=['#2b6cb0'])
            st.plotly_chart(fig_mes, use_container_width=True)
        else:
            st.info("Gráfico no disponible: Falta columna 'MES' en el Excel.")

    st.markdown("---")
    
    # === SECCIÓN 3: TABLA DE DATOS ===
    st.write("### Detalle de Expedientes")
    st.dataframe(datos, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar el archivo Excel: {e}")