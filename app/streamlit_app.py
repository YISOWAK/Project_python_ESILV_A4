import streamlit as st
import yfinance as yf
import pandas as pd
import time
import glob
import os
import plotly.graph_objects as go
from datetime import datetime
import pytz 

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Accueil Quant-A", page_icon="⚡")

# --- FONCTIONS UTILITAIRES ---
def get_paris_time():
    tz_paris = pytz.timezone('Europe/Paris')
    return datetime.now(tz_paris).strftime('%H:%M:%S')

@st.cache_data(ttl=300)
def get_data(symbol, period, interval):
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        if data.empty:
            return pd.DataFrame()

        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        st.error(f"Erreur data : {e}")
        return pd.DataFrame()

def get_latest_report():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(current_dir)
    reports_dir = os.path.join(repo_dir, 'reports')

    if not os.path.exists(reports_dir):
        return f"⚠️ Dossier introuvable : {reports_dir}"

    list_of_files = glob.glob(os.path.join(reports_dir, '*.txt'))
    if not list_of_files:
        return "⚠️ Aucun rapport trouvé."

    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Erreur lecture : {e}"

# --- INTERFACE LIVE (Fragment) ---
# On passe les paramètres (symbol, etc.) comme arguments à la fonction
@st.fragment(run_every=300)
def afficher_dashboard_live(symbol, period, interval):
    
    # Header & Chrono
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title(f"⚡ Terminal Financier : {symbol.split('-')[0]}")
        st.caption("Live Market Data | Auto-Refresh activé (5 min)")

    with c2:
        st.metric(label="Dernière synchro (Paris)", value=get_paris_time())

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📈 Marché (Live)", "📝 Dernier Rapport IA", "ℹ️ Système"])

    with tab1:
        df = get_data(symbol, period, interval)

        if not df.empty:
            last_price = df['Close'].iloc[-1].item()
            prev_price = df['Close'].iloc[-2].item()
            variation = last_price - prev_price
            pct_var = (variation / prev_price) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric(f"Prix {symbol}", f"${last_price:,.2f}", f"{pct_var:+.2f}%")
            col2.metric("Haut", f"${df['High'].max().item():,.2f}")
            col3.metric("Bas", f"${df['Low'].min().item():,.2f}")

            st.subheader(f"Graphique ({interval})")
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
            )])
            fig.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0), xaxis_rangeslider_visible=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Données non disponibles pour ce ticker.")

    with tab2:
        st.header("Synthèse Stratégique")
        st.text(get_latest_report())

    with tab3:
        st.success("Système en ligne")

# --- LANCEMENT ---
if __name__ == "__main__":
    # 1. SIDEBAR (À l'extérieur du fragment !)
    st.sidebar.header("Configuration")
    
    CRYPTO_LIST = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD"]
    sel_symbol = st.sidebar.selectbox("Actif Crypto", CRYPTO_LIST, index=0)

    c1_s, c2_s = st.sidebar.columns(2)
    with c1_s:
        sel_period = st.selectbox("Période", ["1d", "5d", "1mo", "6mo", "1y"], index=2)
    with c2_s:
        sel_interval = st.selectbox("Intervalle", ["15m", "30m", "1h", "4h", "1d"], index=2)
    
    st.sidebar.markdown("---")

    # 2. APPEL DU FRAGMENT
    # On lui envoie les choix de l'utilisateur
    afficher_dashboard_live(sel_symbol, sel_period, sel_interval)