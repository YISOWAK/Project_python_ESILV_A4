import streamlit as st
import yfinance as yf
import pandas as pd
import time
import glob
import os
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Crypto Dashboard Pro", page_icon="💎")

# --- LOGIQUE AUTO-REFRESH (5 Min) ---
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

time_since_last_run = time.time() - st.session_state.last_run
minutes_since_run = int(time_since_last_run // 60)
seconds_since_run = int(time_since_last_run % 60)

if time_since_last_run > 300: # 300 secondes = 5 min
    st.session_state.last_run = time.time()
    st.rerun()

# --- FONCTIONS ---
@st.cache_data(ttl=300) # Cache les données pour 5 min
def get_data(symbol="BTC-USD", period="1mo", interval="1h"):
    data = yf.download(symbol, period=period, interval=interval)
    
    # --- FIX CRITIQUE POUR YFINANCE ---
    # Si les colonnes sont complexes (ex: ('Close', 'BTC-USD')), on les aplatit
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # On s'assure que l'index est bien au format Date
    data.index = pd.to_datetime(data.index)
    # ----------------------------------
    
    return data

def get_latest_report():
    # Cherche tous les fichiers txt dans le dossier reports
    list_of_files = glob.glob('reports/*.txt') 
    if not list_of_files:
        return "Aucun rapport disponible pour le moment."
    # Trouve le plus récent
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return f.read()

# --- INTERFACE ---

# Titre et Header
c1, c2 = st.columns([3, 1])
with c1:
    st.title("⚡ Terminal Financier Quant-A")
    st.caption("Live Market Data | Powered by Yahoo Finance & AWS")
with c2:
    # Ton idée : Le Chrono (Affiché comme une info statique propre)
    st.info(f"⏱️ Actualisé il y a {minutes_since_run}m {seconds_since_run}s\n\nProchain refresh : dans {5 - minutes_since_run} min")

# Onglets pour organiser la page
tab1, tab2, tab3 = st.tabs(["📈 Marché (Live)", "📝 Rapports Journaliers", "ℹ️ Système"])

with tab1:
    # 1. Les Métriques (KPIs)
    df = get_data()
    if not df.empty:
        last_price = df['Close'].iloc[-1].item()
        prev_price = df['Close'].iloc[-2].item()
        variation = last_price - prev_price
        pct_var = (variation / prev_price) * 100
        
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        col_metric1.metric("Bitcoin (BTC)", f"${last_price:,.2f}", f"{pct_var:.2f}%")
        col_metric2.metric("Plus Haut (30j)", f"${df['High'].max().item():,.2f}")
        col_metric3.metric("Plus Bas (30j)", f"${df['Low'].min().item():,.2f}")

        # 2. Le Graphique Pro (Candlestick)
        st.subheader("Analyse Technique")
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'])])
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("📑 Dernier Rapport d'Analyse (Généré par Cron)")
    st.markdown("Ce rapport est généré automatiquement chaque soir à 20h00 par le serveur.")
    
    report_content = get_latest_report()
    
    # Affichage style "Code" pour garder le formatage
    st.code(report_content, language="text")
    
    if st.button("🔄 Forcer la génération d'un rapport (Test)"):
        os.system("./venv/bin/python daily_report.py") # Lance le script
        st.success("Rapport généré ! Rechargez la page.")
        time.sleep(2)
        st.rerun()

with tab3:
    st.write("### État du Système")
    st.write(f"- **Serveur :** AWS EC2 (Ubuntu)")
    st.write(f"- **Processus :** Running (Nohup)")
    st.write(f"- **Port :** 8501")
    st.progress(min(time_since_last_run / 300, 1.0), text="Cycle d'actualisation des données")