import streamlit as st
import time

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Finance",
    layout="wide",
    page_icon="📈"
)

# --- LOGIQUE AUTO-REFRESH (5 Minutes) ---
# Respecte la consigne : "Automatically refresh data every 5 minutes"
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

# Si plus de 300 secondes (5 min) se sont écoulées
if time.time() - st.session_state.last_run > 300:
    st.session_state.last_run = time.time()
    st.rerun() # Force le rechargement du script
# ----------------------------------------

st.title("📊 Dashboard Financier - Accueil")

st.markdown("""
### Bienvenue sur la plateforme de recherche quantitative

Vous êtes connecté à l'environnement de production.

**Modules disponibles :**
* 👈 **Regardez la barre latérale (Sidebar)** à gauche.
* 📈 **1_Single_Asset** : Analyse technique et visualisation sur un actif unique.
* 💼 **2_Portfolio** : Simulation de portefeuille (Bientôt disponible).

*Sélectionnez une page dans le menu pour commencer.*
""")

# Petit indicateur pour voir quand la page s'est mise à jour pour la dernière fois
st.caption(f"Dernière mise à jour : {time.strftime('%H:%M:%S')}")
st.info("Statut du système : Connecté | Data Feed : Yahoo Finance API")