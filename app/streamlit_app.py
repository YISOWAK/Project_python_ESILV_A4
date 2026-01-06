import streamlit as st
import yfinance as yf
import pandas as pd
import time
import glob
import os
import plotly.graph_objects as go
from datetime import datetime
import pytz # Nécessaire pour gérer les fuseaux horaires

# --- CONFIGURATION ---
# On renomme le titre de la page pour le navigateur
st.set_page_config(layout="wide", page_title="Accueil Quant-A", page_icon="⚡")

# --- FONCTIONS UTILITAIRES ---

# Fonction pour récupérer l'heure de Paris ( corrige le décalage d'une heure)
def get_paris_time():
    tz_paris = pytz.timezone('Europe/Paris')
    return datetime.now(tz_paris).strftime('%H:%M:%S')

@st.cache_data(ttl=300)
def get_data(symbol, period, interval):
    """Récupère les données financières via yfinance."""
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)

        # Fix pour yfinance (si MultiIndex sur les colonnes)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if data.empty:
            st.error(f"Aucune donnée récupérée pour {symbol}. Vérifiez les paramètres.")
            return pd.DataFrame()

        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()


def get_latest_report():
    """Cherche et lit le fichier .txt le plus récent dans le dossier 'reports' voisin."""
    # Chemin absolu vers le dossier de l'application courante
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Remonter d'un cran vers le dossier racine du repo
    repo_dir = os.path.dirname(current_dir)
    # Cibler le dossier 'reports'
    reports_dir = os.path.join(repo_dir, 'reports')

    # Vérifie si le dossier existe
    if not os.path.exists(reports_dir):
        return f"⚠️ Dossier introuvable : {reports_dir}"

    # Cherche les fichiers .txt
    list_of_files = glob.glob(os.path.join(reports_dir, '*.txt'))

    if not list_of_files:
        return "⚠️ Aucun rapport journalier trouvé. (Vérifiez que le script Cron tourne)."

    # Trouve le plus récent
    latest_file = max(list_of_files, key=os.path.getctime)

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Erreur de lecture du fichier : {e}"


# --- INTERFACE LIVE (Fragment) ---
# run_every=300 : Rafraîchissement automatique toutes les 5 minutes
@st.fragment(run_every=300)
def afficher_dashboard_live():

    # --- 1. Sidebar (Contrôles) ---
    # On place les contrôles dans le fragment pour qu'ils déclenchent la mise à jour
    st.sidebar.header("Configuration")

    # Choix des actifs (tu peux en ajouter d'autres dans la liste)
    CRYPTO_LIST = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD"]
    selected_symbol = st.sidebar.selectbox("Actif Crypto", CRYPTO_LIST, index=0)

    # Choix de la période et de l'intervalle
    c1_side, c2_side = st.sidebar.columns(2)
    with c1_side:
        # Options courantes pour yfinance
        selected_period = st.selectbox("Période Globale", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd", "max"], index=2) # Défaut '1mo'
    with c2_side:
        # Options d'intervalle (attention aux combinaisons impossibles, ex: 1m sur 1y)
        selected_interval = st.selectbox("Intervalle Bougies", ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1wk"], index=4) # Défaut '1h'

    st.sidebar.markdown("---")


    # --- 2. Header & Chrono ---
    c1, c2 = st.columns([3, 1])
    with c1:
        # Le titre s'adapte à la crypto choisie
        st.title(f"⚡ Terminal Financier : {selected_symbol.split('-')[0]}")
        st.caption("Live Market Data | Auto-Refresh activé (5 min)")

    with c2:
        # Affiche l'heure corrigée de Paris
        maintenant_paris = get_paris_time()
        # Utilisation de st.metric pour un affichage plus propre de l'heure
        st.metric(label="Dernière synchro (Paris)", value=maintenant_paris)


    # --- 3. Les Onglets Principaux ---
    tab1, tab2, tab3 = st.tabs(["📈 Marché (Live)", "📝 Dernier Rapport IA", "ℹ️ Système"])

    # --- ONGLET 1 : MARCHE ---
    with tab1:
        # Appel de la fonction avec les paramètres de la sidebar
        df = get_data(selected_symbol, selected_period, selected_interval)

        if not df.empty:
            # KPI Metrics (Calculs sur la dernière bougie clôturée)
            try:
                last_price = df['Close'].iloc[-1].item()
                prev_price = df['Close'].iloc[-2].item()
                variation = last_price - prev_price
                pct_var = (variation / prev_price) * 100

                # Calcul des stats sur la période affichée
                period_high = df['High'].max().item()
                period_low = df['Low'].min().item()

                col1, col2, col3 = st.columns(3)
                col1.metric(f"Prix {selected_symbol.split('-')[0]}", f"${last_price:,.2f}", f"{pct_var:+.2f}%")
                col2.metric(f"Plus Haut ({selected_period})", f"${period_high:,.2f}")
                col3.metric(f"Plus Bas ({selected_period})", f"${period_low:,.2f}")

            except IndexError:
                st.warning("Pas assez de données pour calculer les variations.")

            # --- Graphique Amélioré ---
            st.subheader(f"Analyse Technique ({selected_interval})")

            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Prix"
            )])

            # Configuration du layout pour le zoom
            fig.update_layout(
                height=550,
                margin=dict(l=10, r=10, t=30, b=10),
                xaxis_rangeslider_visible=True, # Ajoute le slider en bas
                xaxis_title=None,
                yaxis_title="Prix ($)",
                # Permet de zoomer avec la molette et de se déplacer en glissant
                dragmode='pan',
            )

            # Affichage avec activation du scrollZoom dans la config
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={'scrollZoom': True, 'displayModeBar': True}
            )

    # --- ONGLET 2 : RAPPORTS (Nettoyé) ---
    with tab2:
        st.header("Synthèse Stratégique Journalière")
        report_content = get_latest_report()

        if "⚠️" in report_content:
            st.warning(report_content)
        else:
            # Affiche le rapport dans une zone de texte propre
            st.write(report_content)

    # --- ONGLET 3 : SYSTEME ---
    with tab3:
        st.success("Système Opérationnel")
        st.write("Ce tableau de bord utilise la technologie `@st.fragment` de Streamlit.")
        st.write("Il ne recharge que la partie nécessaire de l'interface toutes les 5 minutes ou lors d'un changement de paramètre dans la barre latérale, économisant ainsi des ressources.")


# --- LANCEMENT ---
# On appelle la fonction principale pour lancer l'interface
if __name__ == "__main__":
    afficher_dashboard_live()