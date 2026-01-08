# app/core/predictions.py
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_linear_regression(df: pd.DataFrame, days_ahead: int = 5):
    """
    Entraîne une régression linéaire sur les 30 derniers points (Tendance locale).
    """
    # --- CORRECTION ICI : On ne garde que les 30 derniers points ---
    # Cela permet au modèle de coller au prix actuel ("Momentum")
    df_ml = df[['Close']].tail(30).copy() 
    
    # Le reste ne change pas...
    df_ml['Day_ID'] = np.arange(len(df_ml))
    
    X = df_ml[['Day_ID']]
    y = df_ml['Close']
    
    # Entraînement
    model = LinearRegression()
    model.fit(X, y)
    
    # Préparation des jours futurs pour la prédiction
    last_day_id = df_ml['Day_ID'].iloc[-1]
    future_days_id = np.array([last_day_id + i for i in range(1, days_ahead + 1)]).reshape(-1, 1)
    
    # Prédiction
    future_prices = model.predict(future_days_id)
    
    # Génération des dates futures pour l'affichage
    last_date = df.index[-1]
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days_ahead + 1)]
    
    # Détection de la tendance
    current_price = df['Close'].iloc[-1]
    predicted_final_price = future_prices[-1]
    trend = "Hausse ↗️" if predicted_final_price > current_price else "Baisse ↘️"
    
    return future_dates, future_prices, trend