# Application de simulation énergétique d'un climatiseur

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/votre-utilisateur/votre-depot/main/streamlit_app.py)

Ce projet propose une application web interactive (déployable sur **Streamlit Cloud**) permettant de simuler le comportement d'un système de climatisation dans un bâtiment. L'application compare deux scénarios (référence vs optimisé) afin d'évaluer l'impact de l'amélioration de l'isolation, des vitrages, de la ventilation, etc., sur la consommation d'énergie de la climatisation.

## Fonctionnalités

- **Import de données météo (.EPW)** – Un fichier météo horaire au format EPW peut être importé (un fichier d'exemple `data/exemple_meteo.epw` est fourni).
- **Paramétrage du bâtiment** – Interface en français pour choisir le niveau d'isolation, la performance des vitrages, le taux de ventilation/infiltration et les charges internes (chaque paramètre avec trois choix: faible, moyen, élevé, avec valeurs par défaut cohérentes).
- **Comparaison de deux scénarios** – Simulation parallèle d'un scénario *baseline* (état initial) et d'un scénario *optimisé* (améliorations choisies) pour quantifier les économies d'énergie.
- **Modèle thermique 1R1C** – Calcul du bilan thermique horaire de la zone à l'aide d'un modèle simplifié 1R1C (une résistance, un condensateur) conforme aux normes [ISO 13790](https://www.iso.org/standard/41974.html) / [ISO 52016-1:2017](https://www.iso.org/standard/65696.html).
- **Climatiseur à COP variable** – Modélisation simplifiée d'un climatiseur dont le coefficient de performance (COP) dépend de la température extérieure (efficacité réduite par forte chaleur).
- **Visualisation graphique** – Graphiques interactifs montrant l'évolution de la température extérieure, de la puissance de refroidissement (kW) et de l'énergie cumulée consommée (kWh) pour les deux scénarios tout au long de l'année.
- **Export des résultats** – Bouton de téléchargement pour exporter les résultats complets des simulations au format CSV.
- **Analyse automatique par IA** – Intégration optionnelle de l'API *DeepSeek* (basée sur OpenAI) pour générer une analyse textuelle des résultats. *(Nécessite de renseigner `openai_api_key` et `openai_base_url` dans les secrets Streamlit.)*

## Installation

Assurez-vous d'avoir Python 3.9+ installé. Clonez ce dépôt GitHub, puis installez les dépendances :

```bash
pip install -r requirements.txt
