import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from app.core.config import ASSETS
from app.core.portfolio import build_prices_matrix, simulate_portfolio, normalize_weights
from app.core.metrics import max_drawdown, annualized_return, annualized_vol, sharpe_ratio, corr_matrix

st.set_page_config(layout="wide", page_title="Quant-B Portfolio", page_icon="📊")

# Auto-refresh every 5 minutes (safe + simple)
st.caption("Auto-refresh every 5 minutes (cache TTL = 300s).")


@st.cache_data(ttl=300)
def cached_prices(keys, period, interval):
    return build_prices_matrix(keys, period=period, interval=interval)


def main():
    st.title("📊 Quant-B — Multi-Asset Portfolio")
    st.caption("Source: Yahoo Finance (yfinance) • Auto-refresh: 5 minutes")

    # ---------- Sidebar ----------
    st.sidebar.header("Portfolio settings")

    available_keys = list(ASSETS.keys())
    selected = st.sidebar.multiselect(
        "Select assets (min 3)",
        available_keys,
        default=available_keys[:3],
    )

    period = st.sidebar.selectbox("Period", ["7d", "1mo", "3mo", "6mo", "1y"], index=0)
    interval = st.sidebar.selectbox("Interval", ["5m", "15m", "1h", "4h", "1d"], index=0)
    rebalance = st.sidebar.selectbox("Rebalancing frequency", ["D", "W", "M"], index=1)

    if len(selected) < 3:
        st.warning("Please select at least 3 assets to build a portfolio.")
        return

    # ---------- Weights ----------
    st.sidebar.subheader("Allocation")
    mode = st.sidebar.radio("Mode", ["Equal-weight", "Custom"], index=0)

    if mode == "Equal-weight":
        weights = {k: 1.0 / len(selected) for k in selected}
    else:
        raw = {}
        for k in selected:
            raw[k] = st.sidebar.number_input(
                f"{k} weight",
                min_value=0.0,
                max_value=1.0,
                value=1.0 / len(selected),
                step=0.05,
            )
        weights = normalize_weights(raw)
        st.sidebar.caption(f"Normalized sum = {sum(weights.values()):.2f}")

    # ---------- Data ----------
    prices = cached_prices(tuple(selected), period, interval)
    if prices.empty:
        st.error("No data available. Try another period/interval.")
        return

    returns = prices.pct_change().dropna()
    corr = corr_matrix(returns)


    # ---------- Portfolio simulation ----------
    sim = simulate_portfolio(prices, weights, rebalance=rebalance, base=100.0)
    if sim.empty:
        st.error("Portfolio simulation failed.")
        return

    port_r = sim["Portfolio_Returns"]
    
        # Diversification effect (simple)
    asset_vols = returns.std() * 100.0
    avg_asset_vol = float(asset_vols.mean())
    port_vol = float(port_r.std() * 100.0)

    c5, c6 = st.columns(2)
    c5.metric("Avg asset vol (period)", f"{avg_asset_vol:.2f}%")
    c6.metric("Portfolio vol (period)", f"{port_vol:.2f}%")

    # ---------- KPIs ----------
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Avg asset vol (period)", f"{avg_asset_vol:.2f}%")
    k2.metric("Portfolio vol (period)", f"{port_vol:.2f}%")
    k3.metric("Annualized Return", f"{annualized_return(port_r):.2f}%")
    k4.metric("Annualized Volatility", f"{annualized_vol(port_r):.2f}%")
    k5.metric("Sharpe (rf=0)", f"{sharpe_ratio(port_r):.2f}")
    k6.metric("Max Drawdown", f"{max_drawdown(sim['Portfolio_Equity']):.2f}%")


    # ---------- Main chart ----------
    st.subheader("Normalized prices & Portfolio equity")

    norm = prices / prices.iloc[0] * 100.0
    fig = go.Figure()

    for col in norm.columns:
        fig.add_trace(go.Scatter(x=norm.index, y=norm[col], mode="lines", name=f"{col} (base 100)"))

    fig.add_trace(go.Scatter(
        x=sim.index, y=sim["Portfolio_Equity"],
        mode="lines", name="Portfolio Equity", line=dict(width=4)
    ))

    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # ---------- Correlation matrix ----------
    st.subheader("Correlation matrix (returns)")
    if not corr.empty:
        st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto"), use_container_width=True)
    else:
        st.info("Not enough data to compute correlation matrix.")

    # Small debug expander (optional, pro for robustness)
    with st.expander("Data details"):
        st.write("Last timestamps:", prices.index[-3:])
        st.write("Weights:", weights)

if __name__ == "__main__":
    main()

