import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Taxi Trip Explorer", layout="wide", page_icon="🚖")

st.title("🚖 Taxi Trip Explorer")
st.markdown("Explora viajes de taxi en NYC y descubre patrones útiles para análisis urbano y económico.")

# ----------------------------
# CARGA Y LIMPIEZA DE DATOS
# ----------------------------
@st.cache_data
def load_data(uploaded_file=None):
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("✅ Datos cargados desde el archivo subido por el usuario.")
        else:
            # Posibles rutas relativas
            BASE_DIR = os.path.dirname(__file__)
            possible_paths = [
                os.path.join(BASE_DIR, "datasets", "taxi_data.csv"),
                "datasets/taxi_data.csv",
                "taxi_data.csv"
            ]
            
            df = None
            for path in possible_paths:
                try:
                    df = pd.read_csv(path)
                    st.success(f"✅ Datos cargados correctamente desde: {path}")
                    break
                except FileNotFoundError:
                    continue
            
            if df is None:
                st.info("⚠️ No se encontró el archivo 'taxi_data.csv'. Sube un archivo para continuar.")
                return pd.DataFrame()

        # Limpieza y preprocesamiento
        if 'tpep_pickup_datetime' in df.columns:
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')

        if 'tpep_dropoff_datetime' in df.columns:
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')

        # Cálculo adicional si hace falta
        if 'trip_distance' in df.columns and 'fare_amount' in df.columns:
            df['fare_per_mile'] = df['fare_amount'] / df['trip_distance'].replace(0, pd.NA)

        # Eliminar columnas vacías o irrelevantes
        df = df.dropna(how='all', axis=1)

        return df

    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return pd.DataFrame()


# ----------------------------
# DASHBOARD - VISUALIZACIONES
# ----------------------------
st.subheader("📈 Insights principales")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Viajes registrados", f"{len(df):,}")
col2.metric("Distancia promedio", f"{df['trip_distance'].mean():.2f} mi")
col3.metric("Duración media", f"{df['trip_duration'].mean():.1f} min")
col4.metric("Ganancia total", f"${df['total_amount'].sum():,.2f}")

# ----------------------------------------
# 📊 Distribución de viajes por hora
# ----------------------------------------
st.subheader("🕒 Frecuencia de viajes por hora del día")
df["hour"] = df["tpep_pickup_datetime"].dt.hour
hourly_counts = df["hour"].value_counts().sort_index()
fig1, ax1 = plt.subplots()
sns.barplot(x=hourly_counts.index, y=hourly_counts.values, palette="plasma", ax=ax1)
ax1.set_title("Viajes por Hora del Día")
ax1.set_xlabel("Hora")
ax1.set_ylabel("Número de Viajes")
st.pyplot(fig1)

# ----------------------------------------
# 💳 Método de pago más usado
# ----------------------------------------
st.subheader("💳 Métodos de pago")
payment_mapping = {
    1: "Credit card", 2: "Cash", 3: "No charge",
    4: "Dispute", 5: "Unknown", 6: "Voided trip"
}
df["payment_type"] = df["payment_type"].map(payment_mapping)
fig2, ax2 = plt.subplots()
df["payment_type"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax2)
ax2.set_ylabel("")
ax2.set_title("Distribución de Métodos de Pago")
st.pyplot(fig2)

# ----------------------------------------
# 💵 Relación entre distancia, duración y total
# ----------------------------------------
st.subheader("📉 Relación entre Distancia, Duración y Total Pagado")
fig3, ax3 = plt.subplots()
sns.scatterplot(
    data=df.sample(1000),
    x="trip_duration", y="total_amount",
    hue="trip_distance", palette="coolwarm", ax=ax3
)
ax3.set_xlabel("Duración (min)")
ax3.set_ylabel("Total pagado (USD)")
ax3.set_title("Costo vs. Duración del viaje")
st.pyplot(fig3)

# ----------------------------------------
# 🗺️ Mapa simple de puntos de recogida
# ----------------------------------------
st.subheader("🗺️ Mapa de recogidas")
if "pickup_latitude" in df.columns and "pickup_longitude" in df.columns:
    map_df = df[["pickup_latitude", "pickup_longitude"]].dropna().sample(n=min(1000, len(df)))
    map_df.columns = ["lat", "lon"]
    st.map(map_df)
else:
    st.warning("No se encontraron columnas de geolocalización para el mapa.")

# ----------------------------------------
# 🔍 Explorador de datos
# ----------------------------------------
with st.expander("🔬 Vista previa de los datos"):
    st.dataframe(df.head(50))
