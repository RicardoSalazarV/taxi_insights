import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -------------------------
# CONFIGURACIÓN INICIAL
# -------------------------
st.set_page_config(
    page_title="Taxi Trip Explorer",
    layout="wide",
    page_icon="🚕"
)

st.title("🚕 Taxi Trip Explorer")
st.markdown("Explora, analiza y visualiza viajes de taxi desde un archivo CSV.")

# -------------------------
# FUNCIONES AUXILIARES
# -------------------------
@st.cache_data
def load_data(source):
    try:
        if isinstance(source, str):
            df = pd.read_csv(source)
        else:
            df = pd.read_csv(source)
        return df
    except Exception as e:
        st.error(f"Error cargando los datos: {e}")
        return None

def analyze_trips(df):
    if "tpep_pickup_datetime" not in df.columns:
        st.warning("No se encuentra la columna 'tpep_pickup_datetime'.")
        return
    
    df["pickup_hour"] = pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour
    hourly_counts = df["pickup_hour"].value_counts().sort_index()

    fig, ax = plt.subplots()
    sns.barplot(x=hourly_counts.index, y=hourly_counts.values, palette="viridis", ax=ax)
    ax.set_xlabel("Hora del día")
    ax.set_ylabel("Número de viajes")
    ax.set_title("Distribución de viajes por hora")
    st.pyplot(fig)

def plot_heatmap(df):
    lat_col = None
    lon_col = None
    for lat_candidate in ['pickup_latitude', 'PULocationLat']:
        if lat_candidate in df.columns:
            lat_col = lat_candidate
            break
    for lon_candidate in ['pickup_longitude', 'PULocationLon']:
        if lon_candidate in df.columns:
            lon_col = lon_candidate
            break

    if lat_col and lon_col:
        map_df = df[[lat_col, lon_col]].dropna().sample(n=min(1000, len(df)))
        map_df.columns = ["lat", "lon"]
        st.map(map_df)
    else:
        st.warning("No se encontraron columnas de latitud/longitud para el mapa.")

# -------------------------
# CARGA DE DATOS
# -------------------------
st.sidebar.header("📁 Fuente de datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV", type=["csv"])
default_file_path = os.path.join("datasets", "taxi_data.csv")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.success("✅ Datos cargados desde archivo subido.")
elif os.path.exists(default_file_path):
    df = load_data(default_file_path)
    st.info(f"📂 Usando archivo por defecto: `{default_file_path}`")
else:
    st.warning("⚠️ No se ha subido archivo y no existe archivo por defecto en la ruta esperada.")
    st.stop()

# -------------------------
# INTERFAZ Y VISUALIZACIONES
# -------------------------
with st.expander("👀 Vista previa del dataset"):
    st.dataframe(df.head())

st.subheader("📌 Métricas Principales")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de viajes", f"{df.shape[0]:,}")
with col2:
    dist_col = 'trip_distance' if 'trip_distance' in df.columns else df.select_dtypes(include='number').columns[0]
    st.metric("Distancia media (mi)", f"{df[dist_col].mean():.2f}")
with col3:
    amount_col = 'total_amount' if 'total_amount' in df.columns else df.select_dtypes(include='number').columns[-1]
    st.metric("Ganancia total (USD)", f"${df[amount_col].sum():,.2f}")

st.subheader("🗺️ Distribución Geográfica de Recogidas")
plot_heatmap(df)

st.subheader("📈 Análisis de Frecuencia por Hora del Día")
analyze_trips(df)
