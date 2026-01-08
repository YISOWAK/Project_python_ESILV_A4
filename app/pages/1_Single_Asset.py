import sys
import os
import streamlit as st
import plotly.graph_objects as go

# Fix des chemins
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.data import get_historical_data
from app.core.config import ASSETS
from app.core.strategies import calculate_buy_and_hold, calculate_ma_crossover
from app.core.predictions import predict_linear_regression
st.set_page_config(page_title="Single Asset Strat", layout="wide")
st.title("🧠 Analyse Stratégique (Quant A)")

# --- SIDEBAR ---
st.sidebar.header("1. Données")
asset = st.sidebar.selectbox("Actif", options=list(ASSETS.keys()))
period = st.sidebar.selectbox("Période", ["7d", "1mo", "3mo", "1y"], index=1)
interval = st.sidebar.selectbox("Intervalle", ["15m", "1h", "1d"], index=1)

st.sidebar.header("2. Stratégie")
strat_name = st.sidebar.selectbox("Type", ["Buy & Hold", "MA Crossover"])

params = {}
if strat_name == "MA Crossover":
    params['short'] = st.sidebar.number_input("Moyenne Courte", 5, 50, 20)
    params['long'] = st.sidebar.number_input("Moyenne Longue", 10, 200, 50)

if st.sidebar.button("Appliquer Stratégie"):
    st.cache_data.clear()

# --- MAIN ---
with st.spinner("Calcul en cours..."):
    # 1. Récupération Data
    df = get_historical_data(asset, period=period, interval=interval)
    
    if not df.empty:
        # 2. Application de la Stratégie
        if strat_name == "Buy & Hold":
            df_strat = calculate_buy_and_hold(df)
        elif strat_name == "MA Crossover":
            df_strat = calculate_ma_crossover(df, params['short'], params['long'])
        
        # 3. Affichage Résultats
        last_equity = df_strat['Strategy_Equity'].iloc[-1]
        perf_pct = (last_equity - 100)
        
        col1, col2 = st.columns(2)
        col1.metric("Prix Actuel", f"${df['Close'].iloc[-1]:,.2f}")
        col2.metric("Performance Stratégie (Base 100)", f"{last_equity:.2f}", f"{perf_pct:+.2f}%")
        
        # 4. Graphique Comparatif
        fig = go.Figure()
        
        # Ligne 1 : Prix de l'actif (échelle de gauche)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], 
            name="Prix Actif", 
            line=dict(color='white', width=1),
            yaxis='y1'
        ))
        
        # Ligne 2 : Portefeuille Stratégie (échelle de droite pour bien comparer)
        fig.add_trace(go.Scatter(
            x=df.index, y=df_strat['Strategy_Equity'], 
            name=f"Stratégie {strat_name}",
            line=dict(color='#2E91E5', width=2),
            yaxis='y2'
        ))

        # Double axe Y (Prix à gauche, Performance à droite)
        fig.update_layout(
            title=f"Comparaison Prix vs Stratégie ({strat_name})",
            yaxis=dict(title="Prix ($)", side="left"),
            yaxis2=dict(title="Valeur Portefeuille (Base 100)", side="right", overlaying="y"),
            height=600,
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Voir données calculées"):
            st.dataframe(df_strat.tail(10))

    else:
        st.error("Pas de données.")

    with st.expander("🔮 Bonus : Prédiction ML (Tendance future)", expanded=False):
        st.write("Modèle : Régression Linéaire simple sur l'historique chargé.")
        
        try:
            # APPEL DE LA FONCTION DÉLOCALISÉE (Backend)
            f_dates, f_prices, trend = predict_linear_regression(df, days_ahead=5)
            
            # Affichage résultat (Frontend)
            col_pred1, col_pred2 = st.columns([1, 3])
            with col_pred1:
                st.info(f"Prédiction J+5 : **${f_prices[-1]:,.2f}**")
                st.metric("Tendance détectée", trend)
                
            with col_pred2:
                # Petit graph rapide
                fig_pred = go.Figure()
                # Historique récent (30 derniers points)
                fig_pred.add_trace(go.Scatter(
                    x=df.index[-30:], y=df['Close'].tail(30), 
                    name="Historique", line=dict(color='#B0B0B0')
                ))
                # Futur
                fig_pred.add_trace(go.Scatter(
                    x=f_dates, y=f_prices, 
                    name="Prédiction ML", line=dict(color='yellow', dash='dot')
                ))
                fig_pred.update_layout(
                    height=300, 
                    margin=dict(t=0, b=0, l=0, r=0),
                    showlegend=True
                )
                st.plotly_chart(fig_pred, use_container_width=True)
                
        except Exception as e:
            st.error(f"Erreur lors de la prédiction : {e}")
        