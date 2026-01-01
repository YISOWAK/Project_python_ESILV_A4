import yfinance as yf
import pandas as pd
import streamlit as st
from app.core.config import ASSETS, RETRIES, TIMEOUT

def get_historical_data(symbol_key, period="7d", interval="5m"):
    """
    Récupère les données historiques pour un actif donné.
    
    Args:
        symbol_key (str): La clé de l'actif (ex: 'BTC', 'ETH') définie dans config.py
        period (str): La période d'historique (ex: '7d', '1mo')
        interval (str): L'intervalle des bougies (ex: '5m', '1h')
        
    Returns:
        pd.DataFrame: DataFrame avec les colonnes Open, High, Low, Close, Volume
    """
    # 1. Récupérer le symbole Yahoo Finance depuis la config
    ticker = ASSETS.get(symbol_key)
    if not ticker:
        st.error(f"Erreur : L'actif '{symbol_key}' n'est pas configuré.")
        return pd.DataFrame()

    # 2. Tentative de téléchargement avec retries
    df = pd.DataFrame()
    for i in range(RETRIES):
        try:
            # Téléchargement silencieux (pas de print dans la console)
            df = yf.download(ticker, period=period, interval=interval, progress=False, timeout=TIMEOUT)
            
            # Si on a des données, on arrête la boucle
            if not df.empty:
                break
        except Exception as e:
            print(f"Tentative {i+1} échouée pour {ticker}: {e}")
    
    # 3. Vérification finale
    if df.empty:
        st.warning(f"Aucune donnée récupérée pour {symbol_key} (Yahoo Finance peut être instable).")
        return df

    # 4. Nettoyage des données
    # Yahoo renvoie parfois un MultiIndex difficile à gérer, on le simplifie
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    # On s'assure que les colonnes sont propres
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    # On s'assure que l'index est bien un datetime UTC (important pour comparer)
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    else:
        df.index = df.index.tz_convert('UTC')
        
    return df

def get_latest_price(symbol_key):
    """Récupère juste le dernier prix pour l'affichage temps réel."""
    df = get_historical_data(symbol_key, period="1d", interval="5m")
    if not df.empty:
        return df['Close'].iloc[-1]
    return 0.0