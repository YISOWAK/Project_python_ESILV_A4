import streamlit as st
import yfinance as yf
import pandas as pd
import time
import glob
import os
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Crypto Dashboard Pro", page_icon="💎")

# --- FONCTIONS ---
@st.cache_data(ttl=300) 
def get_data(symbol="BTC-USD", period="1mo", interval="1h"):
    data = yf.download(symbol, period=period, interval=interval)
    
    # Fix pour yfinance (Graphique plat)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data.index = pd.to_datetime(data.index)
    return data

def get_latest_report():
    # --- FIX CHEMIN ABSOLU ---
    # On récupère le chemin exact du dossier "repo"
    current_dir = os.path.dirname(os.path.abspath(__file__)) # dossier app/
    repo_dir = os.path.dirname(current_dir) # dossier repo/ (un cran au-dessus)
    reports_dir = os.path.join(repo_dir, 'reports')
    
    # Vérifie si le dossier existe
    if not os.path.exists(reports_dir):
        return f"⚠️ Dossier introuvable : {reports_dir}"

    # Cherche les fichiers
    list_of_files = glob.glob(os.path.join(reports_dir, '*.txt')) 
    
    if not list_of_files:
        return "⚠️ Aucun rapport trouvé. (Le Cron tourne-t-il ?)"
    
    # Trouve le plus récent
    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return f.read()

# --- INTERFACE LIVE (Fragment) ---
# C'est ICI la magie : run_every=300 signifie "Recharge cette fonction toutes les 300s (5min)"
@st.fragment(run_every=300)
def afficher_dashboard_live():
    
    # 1. Header & Chrono
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("⚡ Terminal Financier Quant-A")
        st.caption("Live Market Data | Auto-Refresh activé (5 min)")

    with c2:
        # Affiche l'heure actuelle du serveur pour prouver que ça tourne
        maintenant = time.strftime('%H:%M:%S')
        st.info(f"🔄 Dernière synchro : **{maintenant}**\n\n(S'actualise tout seul)")

    # 2. Les Onglets
    tab1, tab2, tab3 = st.tabs(["📈 Marché (Live)", "📝 Rapports Journaliers", "ℹ️ Système"])

    with tab1:
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

            # Graphique
            st.subheader("Analyse Technique")
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'])])
            fig.update_layout(height=500, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("📑 Dernier Rapport d'Analyse")
        
        if st.button("🔄 Forcer la génération (Test)"):
            # On utilise le chemin relatif car on lance la commande depuis la racine repo
            os.system("./venv/bin/python daily_report.py")
            st.toast("Génération lancée...")
            time.sleep(1)
            st.rerun()

        report_content = get_latest_report()
        st.text_area("Lecture du fichier :", report_content, height=400)

    with tab3:
        st.success("Système Opérationnel")
        st.write("Ce dashboard utilise `@st.fragment` pour se rafraîchir automatiquement.")

# --- LANCEMENT ---
# On appelle la fonction "Live" une première fois
afficher_dashboard_live()