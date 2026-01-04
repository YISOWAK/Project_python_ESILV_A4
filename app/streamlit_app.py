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

# Vérifie si 5 min (300s) sont passées
if time.time() - st.session_state.last_run > 300:
    st.session_state.last_run = time.time()
    st.rerun()

# --- FONCTIONS ---
@st.cache_data(ttl=300) 
def get_data(symbol="BTC-USD", period="1mo", interval="1h"):
    # Téléchargement des données
    data = yf.download(symbol, period=period, interval=interval)
    
    # --- FIX CRITIQUE POUR YFINANCE (Graphique Plat) ---
    # Si les colonnes sont complexes (MultiIndex), on les simplifie
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # On s'assure que l'index est bien une date
    data.index = pd.to_datetime(data.index)
    return data

def get_latest_report():
    # Cherche tous les fichiers txt dans le dossier reports
    # Le chemin est relatif à l'endroit où on lance le script
    list_of_files = glob.glob('reports/*.txt') 
    if not list_of_files:
        return "⚠️ Aucun rapport disponible. Attendez 20h00 ou forcez la génération."
    
    # Trouve le plus récent
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return f.read()

# --- INTERFACE ---

# 1. Header & Chrono
c1, c2 = st.columns([3, 1])
with c1:
    st.title("⚡ Terminal Financier Quant-A")
    st.caption("Live Market Data | Powered by Yahoo Finance & AWS")

with c2:
    # --- LE NOUVEAU CHRONO (Plus clair) ---
    # Calcule l'heure de la prochaine mise à jour
    prochain_refresh = time.strftime('%H:%M', time.localtime(st.session_state.last_run + 300))
    st.info(f"✅ Données à jour.\n\n🔄 Prochain refresh auto : **{prochain_refresh}**")

# 2. Les Onglets
tab1, tab2, tab3 = st.tabs(["📈 Marché (Live)", "📝 Rapports Journaliers", "ℹ️ Système"])

with tab1:
    # --- Onglet Graphique ---
    df = get_data()
    
    if not df.empty:
        # KPI Metrics
        last_price = df['Close'].iloc[-1].item()
        prev_price = df['Close'].iloc[-2].item()
        variation = last_price - prev_price
        pct_var = (variation / prev_price) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Bitcoin (BTC)", f"${last_price:,.2f}", f"{pct_var:.2f}%")
        col2.metric("Plus Haut (30j)", f"${df['High'].max().item():,.2f}")
        col3.metric("Plus Bas (30j)", f"${df['Low'].min().item():,.2f}")

        # Graphique Plotly (Bougies)
        st.subheader("Analyse Technique")
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'])])
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Erreur de chargement des données Yahoo Finance.")

with tab2:
    # --- Onglet Rapports ---
    st.header("📑 Dernier Rapport d'Analyse")
    st.markdown("Ce rapport est généré automatiquement par le CRON (tous les jours à 20h00).")
    
    # Bouton pour tester manuellement
    if st.button("🔄 Forcer la génération d'un rapport maintenant"):
        os.system("./venv/bin/python daily_report.py")
        st.toast("Rapport généré ! Rechargement...")
        time.sleep(2)
        st.rerun()

    # Affiche le contenu du fichier
    report_content = get_latest_report()
    st.text_area("Contenu du rapport :", report_content, height=300)

with tab3:
    # --- Onglet Système ---
    st.write("### État du Système")
    st.success("Système Opérationnel (AWS EC2)")
    st.write(f"- **Dernière Synchro :** {time.strftime('%H:%M:%S', time.localtime(st.session_state.last_run))}")