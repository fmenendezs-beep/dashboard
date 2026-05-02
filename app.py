import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Video Game Sales Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("PS,S-A.xlsx")
    return df

df = load_data()

# Title and description
st.title("Video Game Sales Dashboard")
st.markdown("An interactive dashboard analyzing historical video game sales data.")

# Sidebar filters
st.sidebar.header("Filters")
platform_options = ["All"] + sorted(df["Plataforma"].dropna().astype(str).unique().tolist())
selected_platform = st.sidebar.selectbox("Platform", platform_options)
genre_options = ["All"] + sorted(df["Genero"].dropna().astype(str).unique().tolist())
selected_genre = st.sidebar.selectbox("Genre", genre_options)

# Filter dataframe based on selections
filtered_df = df.copy()
if selected_platform != "All":
    filtered_df = filtered_df[filtered_df["Plataforma"] == selected_platform]
if selected_genre != "All":
    filtered_df = filtered_df[filtered_df["Genero"] == selected_genre]

# -- Calculations --
# 1. Ventas globales totales (KPI)
total_global_sales = filtered_df["Ventas Global"].sum()

# 2. Número total de títulos (KPI)
total_titles = len(filtered_df)

# 3. Juego más vendido (KPI or table)
top_game = filtered_df.loc[filtered_df["Ventas Global"].idxmax()] if not filtered_df.empty else None

# 4. Plataforma con más ventas (KPI)
platform_sales = filtered_df.groupby("Plataforma")["Ventas Global"].sum().reset_index()
top_platform = platform_sales.loc[platform_sales["Ventas Global"].idxmax()] if not platform_sales.empty else None

# 5. Editorial con más ventas (KPI)
publisher_sales = filtered_df.groupby("Editorial")["Ventas Global"].sum().reset_index()
top_publisher = publisher_sales.loc[publisher_sales["Ventas Global"].idxmax()] if not publisher_sales.empty else None

# 6. Ventas por región (Gráfico comparativo)
region_sales = {
    "NA Sales": filtered_df["Ventas NA"].sum(),
    "EU Sales": filtered_df["Ventas EU"].sum(),
    "JP Sales": filtered_df["Ventas JP"].sum(),
    "Other Sales": filtered_df["Ventas Otros"].sum()
}
region_df = pd.DataFrame(list(region_sales.items()), columns=["Region", "Sales"])

# 7. Género más vendido (KPI or Gráfico)
genre_sales = filtered_df.groupby("Genero")["Ventas Global"].sum().reset_index()
top_genre = genre_sales.loc[genre_sales["Ventas Global"].idxmax()] if not genre_sales.empty else None

# 8. Promedio de ventas por juego (KPI)
avg_sales_per_game = filtered_df["Ventas Global"].mean()

# 9. Años con más ventas (Gráfico de tendencia)
year_sales = filtered_df.groupby("Año")["Ventas Global"].sum().reset_index()
year_sales = year_sales.sort_values("Año")

# 10. Tasa de ventas en Japón vs Global (Proporción o Gráfico)
total_jp = filtered_df["Ventas JP"].sum()
jp_vs_global_ratio = (total_jp / total_global_sales) * 100 if total_global_sales else 0

# --- Layout ---
# Row 1: KPIs (top row)
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Global Sales (M)", f"{total_global_sales:.2f}")
col2.metric("Total Titles", total_titles)
col3.metric("Average Sales per Game (M)", f"{avg_sales_per_game:.2f}")
col4.metric("JP vs Global Sales Ratio", f"{jp_vs_global_ratio:.1f}%")

# Row 2: Top game, platform, publisher
col5, col6, col7 = st.columns(3)
with col5:
    st.subheader("Top Game")
    if top_game is not None:
        st.write(f"**{top_game['Nombre']}**")
        st.write(f"Sales: {top_game['Ventas Global']} M")
with col6:
    st.subheader("Top Platform")
    if top_platform is not None:
        st.write(f"**{top_platform['Plataforma']}**")
        st.write(f"Sales: {top_platform['Ventas Global']:.2f} M")
with col7:
    st.subheader("Top Publisher")
    if top_publisher is not None:
        st.write(f"**{top_publisher['Editorial']}**")
        st.write(f"Sales: {top_publisher['Ventas Global']:.2f} M")

# Charts
st.subheader("Sales by Region")
fig_region = px.bar(region_df, x="Region", y="Sales", color="Region",
                    title="Global Sales by Region (Millions)")
st.plotly_chart(fig_region, use_container_width=True)

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Sales by Genre")
    fig_genre = px.bar(genre_sales.sort_values("Ventas Global", ascending=False),
                       x="Genero", y="Ventas Global", color="Genero",
                       title="Total Sales by Genre")
    fig_genre.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_genre, use_container_width=True)

with col_right:
    st.subheader("Annual Sales Trend")
    fig_year = px.line(year_sales, x="Año", y="Ventas Global",
                       title="Global Sales Over Years")
    st.plotly_chart(fig_year, use_container_width=True)

# Optional: Detailed table
st.subheader("Top 10 Best-Selling Games")
top10 = filtered_df.nlargest(10, "Ventas Global")[["Nombre", "Plataforma", "Año", "Genero", "Editorial", "Ventas Global"]]
st.dataframe(top10.reset_index(drop=True))