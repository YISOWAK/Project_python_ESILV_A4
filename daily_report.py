import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Configuration
SYMBOL = "BTC-USD"
REPORT_DIR = "reports"

# Créer le dossier reports s'il n'existe pas
os.makedirs(REPORT_DIR, exist_ok=True)

def generate_daily_report():
    print(f"Génération du rapport pour {SYMBOL}...")
    
    # 1. Récupérer les données (1 mois pour la volatilité, 1 jour pour le prix)
    ticker = yf.Ticker(SYMBOL)
    hist = ticker.history(period="1mo")
    
    # 2. Calculs
    today_data = hist.iloc[-1]
    open_price = today_data['Open']
    close_price = today_data['Close']
    
    # Volatilité (écart type des rendements journaliers sur 1 mois)
    hist['Returns'] = hist['Close'].pct_change()
    volatility = hist['Returns'].std() * 100 # En pourcentage
    
    # Max Drawdown (Chute maximale depuis le sommet sur 1 mois)
    rolling_max = hist['Close'].cummax()
    drawdown = (hist['Close'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100 # En pourcentage

    # 3. Création du contenu du rapport
    report_date = datetime.now().strftime("%Y-%m-%d")
    report_content = f"""
    --- RAPPORT JOURNALIER : {SYMBOL} ---
    Date : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    PRIX:
    - Open : ${open_price:.2f}
    - Close: ${close_price:.2f}
    
    RISQUE (30 jours):
    - Volatilité : {volatility:.2f}%
    - Max Drawdown: {max_drawdown:.2f}%
    -------------------------------------
    """
    
    # 4. Sauvegarde
    filename = f"{REPORT_DIR}/report_{report_date}.txt"
    with open(filename, "w") as f:
        f.write(report_content)
    
    print(f"Rapport sauvegardé : {filename}")

if __name__ == "__main__":
    generate_daily_report()