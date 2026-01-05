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
        st.header("🕵️ Debugging du Rapport")
        
        # 1. Où sommes-nous ?
        current_dir = os.getcwd()
        st.write(f"📂 **Dossier de travail actuel (CWD) :** `{current_dir}`")
        
        # 2. Où cherchons-nous les rapports ?
        # On reconstruit le chemin
        base_dir = os.path.dirname(os.path.abspath(__file__)) # Dossier app/
        repo_dir = os.path.dirname(base_dir) # Dossier repo/
        reports_dir = os.path.join(repo_dir, 'reports')
        
        st.write(f"📍 **Chemin ciblé pour les rapports :** `{reports_dir}`")
        
        # 3. Le dossier existe-t-il ?
        if os.path.exists(reports_dir):
            st.success("✅ Le dossier 'reports' EXISTE bien à cet endroit !")
            
            # 4. Qu'il y a-t-il dedans ?
            fichiers = os.listdir(reports_dir)
            st.write("📄 **Fichiers trouvés dans le dossier :**")
            st.write(fichiers)
            
            # 5. Tentative de lecture du dernier fichier
            txt_files = glob.glob(os.path.join(reports_dir, '*.txt'))
            if txt_files:
                latest_file = max(txt_files, key=os.path.getctime)
                st.info(f"Lecture du fichier : {latest_file}")
                with open(latest_file, 'r') as f:
                    st.code(f.read())
            else:
                st.error("❌ Le dossier est vide ou ne contient pas de .txt")
        else:
            st.error("❌ Le dossier 'reports' est INTROUVABLE à cet endroit.")
            st.warning("Essayons de voir ce qu'il y a dans le dossier repo/ :")
            if os.path.exists(repo_dir):
                st.write(os.listdir(repo_dir))

    with tab3:
        st.success("Système Opérationnel")
        st.write("Ce dashboard utilise `@st.fragment` pour se rafraîchir automatiquement.")

# --- LANCEMENT ---
# On appelle la fonction "Live" une première fois
afficher_dashboard_live()