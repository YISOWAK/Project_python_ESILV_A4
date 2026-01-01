import streamlit as st

st.set_page_config(
    page_title="Dashboard Finance",
    layout="wide",
    page_icon="📈"
)

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

st.info("Statut du système : Connecté | Data Feed : Yahoo Finance API")