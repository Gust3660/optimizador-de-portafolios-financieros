"""Interfaz Streamlit para explorar carteras simuladas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from backend import optimize_portfolios


def demo_prices() -> pd.DataFrame:
    rng = np.random.default_rng(11)
    count, assets = 120, 5
    common = rng.normal(0.004, 0.025, count)
    returns = np.column_stack([
        0.002 + beta * common + rng.normal(0, volatility, count)
        for beta, volatility in [(0.5, 0.018), (0.8, 0.022), (1.0, 0.028), (1.2, 0.035), (0.3, 0.012)]
    ])
    prices = 100 * np.cumprod(1 + returns, axis=0)
    dates = pd.date_range("2016-01-31", periods=count, freq="M")
    return pd.DataFrame(prices, columns=["Activo A", "Activo B", "Activo C", "Activo D", "Activo E"]).assign(fecha=dates)


def returns_from_prices(data: pd.DataFrame) -> tuple[list[str], np.ndarray]:
    price_columns = [column for column in data.columns if column != "fecha"]
    prices = data[price_columns].apply(pd.to_numeric, errors="coerce")
    if prices.isna().any().any() or (prices <= 0).any().any():
        raise ValueError("Las columnas de precios deben contener solo números positivos.")
    if len(prices) < 11 or len(price_columns) < 2:
        raise ValueError("Se requieren al menos 11 filas de precios y 2 columnas de activos.")
    return [str(column) for column in price_columns], prices.pct_change().dropna().to_numpy()


st.set_page_config(page_title="Optimizador de portafolios", page_icon="💹", layout="wide")
st.title("Optimizador de portafolios financieros")
st.write("Explora la relación entre rendimiento y riesgo mediante simulación Monte Carlo de carteras diversificadas.")
st.warning("Herramienta educativa basada en datos históricos o sintéticos; no es asesoría financiera ni garantiza rendimientos futuros.")

with st.sidebar:
    source = st.radio("Datos", ["Ejemplo sintético", "Subir precios CSV"])
    upload = st.file_uploader("CSV de precios", type=["csv"]) if source == "Subir precios CSV" else None
    periods_per_year = st.selectbox("Periodos por año", [12, 52, 252], format_func=lambda x: {12: "Mensual · 12", 52: "Semanal · 52", 252: "Diario · 252"}[x])
    risk_free = st.number_input("Tasa libre de riesgo anual", min_value=-0.10, max_value=0.30, value=0.02, step=0.01, format="%.3f")
    simulations = st.slider("Carteras simuladas", 1000, 30000, 10000, 1000)

if source == "Subir precios CSV" and upload is None:
    st.info("Sube una tabla de precios: una columna por activo y al menos 11 filas.")
    st.stop()
try:
    data = demo_prices() if source == "Ejemplo sintético" else pd.read_csv(upload)
    if "fecha" in data.columns:
        data["fecha"] = pd.to_datetime(data["fecha"], errors="coerce")
        if data["fecha"].isna().any():
            raise ValueError("La columna fecha contiene valores no válidos.")
        data = data.sort_values("fecha").reset_index(drop=True)
    asset_names, asset_returns = returns_from_prices(data)
    result = optimize_portfolios(asset_returns, periods_per_year, risk_free, simulations)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(str(error))
    st.stop()

best = result.max_sharpe_index
low_risk = result.min_volatility_index
metrics = st.columns(4)
metrics[0].metric("Mayor Sharpe simulado", f"{result.sharpe[best]:.3f}")
metrics[1].metric("Rendimiento anual estimado", f"{result.annual_returns[best]:.1%}")
metrics[2].metric("Volatilidad anual estimada", f"{result.annual_volatility[best]:.1%}")
metrics[3].metric("Cartera de mínima volatilidad", f"{result.annual_volatility[low_risk]:.1%}")

scatter = pd.DataFrame({"Volatilidad": result.annual_volatility, "Rendimiento": result.annual_returns, "Sharpe": result.sharpe})
left, right = st.columns([2, 1])
left.subheader("Frontera simulada")
left.scatter_chart(scatter, x="Volatilidad", y="Rendimiento", color="Sharpe", use_container_width=True)
selection = st.selectbox("Composición a consultar", ["Mayor Sharpe", "Mínima volatilidad"])
selected_index = best if selection == "Mayor Sharpe" else low_risk
weights_frame = pd.DataFrame({"Activo": asset_names, "Peso": result.weights[selected_index]})
right.subheader(selection)
right.dataframe(weights_frame.style.format({"Peso": "{:.1%}"}), use_container_width=True, hide_index=True)
right.bar_chart(weights_frame.set_index("Activo"))

st.download_button(
    "Descargar pesos CSV",
    weights_frame.to_csv(index=False).encode("utf-8"),
    f"cartera_{'sharpe' if selected_index == best else 'minima_volatilidad'}.csv",
    "text/csv",
)
st.caption(f"Anualización: {periods_per_year} periodos/año · {simulations:,} carteras long-only simuladas.")
