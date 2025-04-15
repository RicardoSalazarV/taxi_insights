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
def load_and_clean_data(path):
    df = pd.read_csv(path)

    # Conversión de fechas
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    
    # Cálculo de duración en minutos
    df["trip_duration"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    
    # Limpieza básica de outliers
    df = df[df["trip_distance"].between(0.5, 50)]
    df = df[df["trip_duration"].between(1, 180)]
    df = df[df["total_amount"] > 0]
    df = df[df["passenger_count"].between(1, 6)]
    
    return df

default_file_path = os.path.join("datasets", "taxi_data.csv")
df = load_and_clean_data(default_file_path)

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
