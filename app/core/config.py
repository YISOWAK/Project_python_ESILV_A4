# app/core/config.py

# Liste des actifs à surveiller (Symboles Yahoo Finance)
ASSETS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",

}

# Paramètres de récupération de données
INTERVAL_DEFAULT = "5m"  # Intervalle prioritaire
PERIOD_DEFAULT = "7d"    # Historique par défaut

# Paramètres techniques
RETRIES = 3              # Nombre d'essais si l'API échoue
TIMEOUT = 10             # Temps max d'attente (secondes)

# Fuseau horaire (Important pour les cron jobs)
TIMEZONE = "Europe/Paris"