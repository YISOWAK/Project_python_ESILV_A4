import sys
import os
import streamlit as st

# --- FIX DU CHEMIN (Le truc magique) ---
# Cela dit à Python : "Regarde deux dossiers en arrière pour trouver les modules"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# ---------------------------------------

import plotly.graph_objects as go
from app.core.data import get_historical_data
from app.core.config import ASSETS

# Configuration de la page
st.set_page_config(page_title="Single Asset Analysis", layout="wide")

st.title("💰 Analyse Actif Unique (Quant A)")

# --- SIDEBAR (Menu de gauche) ---
st.sidebar.header("Paramètres")

# Choix de l'actif
selected_asset_key = st.sidebar.selectbox(
    "Choisir l'actif",
    options=list(ASSETS.keys())
)

# Choix de la période
period = st.sidebar.selectbox(
    "Historique",
    options=["1d", "7d", "1mo", "3mo", "1y"],
    index=1  # Par défaut "7d"
)

# Choix de l'intervalle
interval = st.sidebar.selectbox(
    "Intervalle (Bougies)",
    options=["1m", "5m", "15m", "1h", "1d"],
    index=1 # Par défaut "5m"
)

# --- MAIN CONTENT (Contenu principal) ---

if st.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()

# Chargement des données
with st.spinner(f"Chargement des données pour {selected_asset_key}..."):
    try:
        # On appelle notre fonction data.py
        df = get_historical_data(selected_asset_key, period=period, interval=interval)
        
        if not df.empty:
            # Métriques
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            variation = (last_price - prev_price) / prev_price * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Prix Actuel", f"${last_price:,.2f}", f"{variation:.2f}%")
            col1.caption(f"Dernière mise à jour : {df.index[-1]}")
            
            # Graphique
            st.subheader(f"Évolution du prix : {selected_asset_key}")
            
            fig = go.Figure()
            
            # Bougies (Candlestick)
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Prix"
            ))

            fig.update_layout(height=600, xaxis_title="Date", yaxis_title="Prix ($)")
            st.plotly_chart(fig, use_container_width=True)

            # Debug Data
            with st.expander("Voir les données brutes"):
                st.dataframe(df.tail(10))
                
        else:
            st.error("Aucune donnée disponible. Yahoo Finance bloque peut-être les requêtes.")
            
    except Exception as e:
        st.error(f"Erreur technique : {e}")