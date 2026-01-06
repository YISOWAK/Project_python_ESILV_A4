# Journal de Bord — Projet Finance (ESILV A4)

## Infrastructure & Setup

- [x] Dépôt GitHub créé  
- [x] Dépôt cloné en local  
  - Chemin : `C:\ESILV\A4\Linux,git,python\Projet`
- [x] Structure des dossiers définie (`app/`, `core/`, `pages/`, `docs/`)
- [x] Fichier `requirements.txt` créé
- [x] Clé SSH localisée  
  - `C:\Users\antoi\Downloads\finance-key.pem`
- [x] Configuration AWS :
  - Security Group configuré
  - Port **8501** ouvert (Streamlit)

---

## Backend — Data & Calculs

- [x] Test du module de récupération de données  
  - Source : Yahoo Finance (`yfinance`)
  - Résultat : **Sanity check OK (BTC data reçue)**
- [ ] Script `daily_report.py`  
  - Génération d’un rapport journalier (volatilité, open/close, drawdown)
  - Heure cible : **20h**
- [ ] Mise en place du **cron job** sur la VM Linux  
  - Exécution automatique quotidienne
  - Stockage local dans `/reports`

---

## Frontend — Application Streamlit

- [x] Interface Streamlit de base fonctionnelle
- [x] Affichage du prix et graphique principal
- [ ] **URGENT** — Mise en place de l’auto-refresh  
  - Rafraîchissement toutes les **5 minutes**
  - Option : `@st.cache_data(ttl=300)` ou `st.fragment`
- [ ] Implémentation des stratégies Quant A :
  - Buy & Hold
  - Moyennes mobiles (MA crossover)
- [ ] Intégration complète Quant B :
  - Multi-actifs
  - Simulation de portefeuille
  - Rebalancing
  - Métriques de diversification

---

## Déploiement & Exploitation

- [ ] Lancement de l’application en continu (24/7)
- [ ] Exécution persistante via `nohup` ou service systemd
- [ ] Vérification de la stabilité long terme
- [ ] Tests finaux avant évaluation

---

## Notes

- Le projet suit une organisation proche d’un workflow professionnel en Asset Management.
- La séparation Quant A / Quant B est respectée via des modules dédiés.
- L’objectif final est une plateforme robuste, lisible et exploitable en continu sur une VM Linux.
