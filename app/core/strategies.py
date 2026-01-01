import pandas as pd
import numpy as np

def calculate_buy_and_hold(df):
    """
    Stratégie simple : On achète au début et on ne touche plus.
    Renvoie le DF avec une colonne 'Strategy_Equity' (Portefeuille).
    """
    df = df.copy()
    
    # Calcul des rendements quotidiens (variation en %)
    df['Returns'] = df['Close'].pct_change()
    
    # On remplace les trous par 0
    df['Returns'] = df['Returns'].fillna(0)
    
    # Calcul de la courbe de performance (Base 100 au début)
    # (1 + r1) * (1 + r2) * ...
    df['Strategy_Equity'] = 100 * (1 + df['Returns']).cumprod()
    
    return df

def calculate_ma_crossover(df, short_window=20, long_window=50):
    """
    Stratégie Croisement Moyennes Mobiles.
    Achat (1) quand Courte > Longue.
    Cash (0) quand Courte < Longue.
    """
    df = df.copy()
    
    # 1. Calcul des indicateurs
    df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
    df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
    
    # 2. Génération du Signal (0 ou 1)
    df['Signal'] = 0.0
    # Là où Courte > Longue, on met 1
    df.loc[df['SMA_Short'] > df['SMA_Long'], 'Signal'] = 1.0
    
    # 3. Calcul de la performance
    df['Returns'] = df['Close'].pct_change()
    
    # IMPORTANT : On décale le signal d'un cran (shift 1).
    # On utilise le signal de la VEILLE pour décider d'être investi AUJOURD'HUI.
    # Sinon on triche (Look-ahead bias).
    df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
    df['Strategy_Returns'] = df['Strategy_Returns'].fillna(0)
    
    # Courbe de performance (Base 100)
    df['Strategy_Equity'] = 100 * (1 + df['Strategy_Returns']).cumprod()
    
    return df