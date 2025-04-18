import streamlit as st
import pandas as pd
import altair as alt

# Import des modules de notre package acsim
from acsim import weather, envelope, ventilation, internal_loads, ac_model, thermal_model, scenario, ai_analysis

# Configuration de la page Streamlit
st.set_page_config(page_title="Simulation Climatisation", page_icon="❄️", layout="wide")

# Titre de l'application
st.title("Simulation énergétique d'un climatiseur")

# Description de l'application
st.markdown(
    "Cette application simule le **bilan thermique horaire** d'un bâtiment et la consommation d'énergie d'un **climatiseur** " 
    "pour deux scénarios : un scénario de référence *baseline* et un scénario *optimisé*. "
    "Le modèle thermique utilise un réseau simplifié 1R1C conforme aux normes ISO 13790 / 52016-1. "
    "L'utilisateur peut configurer les paramètres du bâtiment (isolation, vitrage, ventilation, charges internes), "
    "sélectionner un fichier météo au format EPW et comparer les résultats entre les deux scénarios."
)

# Chargement du fichier météo EPW (utilisation d'un exemple par défaut si aucun fichier importé)
st.sidebar.header("Paramètres météorologiques")
uploaded_file = st.sidebar.file_uploader("Fichier météo (.epw)", type=["epw"], help="Importez un fichier météo EPW. Un exemple par défaut est utilisé si aucun fichier n'est fourni.")
if uploaded_file is not None:
    # Lire le fichier EPW importé
    weather_df = weather.read_epw(uploaded_file)
else:
    # Utiliser le fichier météo d'exemple fourni dans data/
    weather_df = weather.read_epw("data/exemple_meteo.epw")
    st.sidebar.write("**Météo :** exemple_meteo.epw utilisé")

# Paramètres généraux
st.sidebar.header("Paramètres généraux du bâtiment")
# Température intérieure de consigne (on suppose un maintien constant par le climatiseur si nécessaire)
T_int = st.sidebar.number_input("Température intérieure de consigne (°C)", min_value=10, max_value=30, value=25)

# Sélections pour les niveaux d'isolation, vitrage, ventilation, charges internes
iso_options = ["Faible", "Moyen", "Élevé"]
vit_options = ["Faible", "Moyen", "Élevé"]
vent_options = ["Faible", "Moyen", "Élevé"]
int_options = ["Faible", "Moyen", "Élevé"]

st.sidebar.subheader("Scénario 1 : Baseline")
iso1 = st.sidebar.selectbox("Isolation", iso_options, index=0, help="Qualité de l'isolation thermique de l'enveloppe (Faible = mauvaise isolation, Élevé = très bonne isolation)")
vit1 = st.sidebar.selectbox("Vitrage", vit_options, index=0, help="Qualité des vitrages et protections solaires (Faible = simple vitrage sans protection, Élevé = double vitrage performant avec protections)")
vent1 = st.sidebar.selectbox("Ventilation / Infiltration", vent_options, index=2, help="Taux de renouvellement d'air (Faible = maison étanche, Élevé = infiltrations élevées)")
int1 = st.sidebar.selectbox("Charges internes", int_options, index=1, help="Importance des apports internes (occupants, équipements)")

st.sidebar.subheader("Scénario 2 : Optimisé")
iso2 = st.sidebar.selectbox("Isolation ", iso_options, index=2, help="Isolation améliorée dans le scénario optimisé", key="iso2")
vit2 = st.sidebar.selectbox("Vitrage ", vit_options, index=2, help="Vitrages améliorés/protections solaires dans le scénario optimisé", key="vit2")
vent2 = st.sidebar.selectbox("Ventilation / Infiltration ", vent_options, index=0, help="Ventilation maîtrisée/infiltrations réduites dans le scénario optimisé", key="vent2")
int2 = st.sidebar.selectbox("Charges internes ", int_options, index=1, help="Apports internes (occupants, appareils) dans le scénario optimisé", key="int2")

# Création des deux scénarios avec les paramètres sélectionnés
scenario1 = scenario.Scenario(isolation=iso1, vitrage=vit1, ventilation=vent1, interne=int1, T_int=T_int)
scenario2 = scenario.Scenario(isolation=iso2, vitrage=vit2, ventilation=vent2, interne=int2, T_int=T_int)

# Simulation des deux scénarios (calcul du bilan thermique horaire et de la consommation clim)
results1 = thermal_model.simuler_scenario(weather_df, scenario1)
results2 = thermal_model.simuler_scenario(weather_df, scenario2)

# Récupération des DataFrames de résultats
df1 = results1['data']
df2 = results2['data']
total_energy1 = results1['total_energy_kWh']
total_energy2 = results2['total_energy_kWh']
peak_power1 = results1['peak_power_kW']
peak_power2 = results2['peak_power_kW']

# Affichage des indicateurs synthétiques
col1, col2, col3 = st.columns(3)
col1.metric("Conso annuelle Scénario 1", f"{total_energy1:.1f} kWh")
col2.metric("Conso annuelle Scénario 2", f"{total_energy2:.1f} kWh")
# Calcul de l'économie en pourcentage, évite division par zéro
if total_energy1 > 0:
    economie = (1 - total_energy2/total_energy1) * 100
else:
    economie = 0.0
col3.metric("Économie estimée", f"{economie:.1f} %")

# Graphique des puissances de refroidissement (kW) sur l'année
st.subheader("Puissance de refroidissement horaire")
power_chart = thermal_model.creer_graphique_puissance(df1, df2)
st.altair_chart(power_chart, use_container_width=True)

# Graphique de l'énergie cumulée (kWh) sur l'année
st.subheader("Énergie cumulée consommée")
energy_chart = thermal_model.creer_graphique_energie(df1, df2)
st.altair_chart(energy_chart, use_container_width=True)

# Graphique des températures extérieure (et intérieure de consigne)
st.subheader("Température extérieure")
temp_chart = thermal_model.creer_graphique_temperature(df1)
st.altair_chart(temp_chart, use_container_width=True)

# Bouton de téléchargement des résultats au format CSV
csv_data = thermal_model.exporter_csv(df1, df2)
st.download_button("Télécharger les résultats (CSV)", data=csv_data, file_name="simulation_clim.csv", mime="text/csv")

# Option d'analyse automatique via l'API DeepSeek (si les clés API sont fournies dans st.secrets)
st.subheader("Analyse automatique des scénarios")
if 'openai_api_key' in st.secrets and 'openai_base_url' in st.secrets:
    if st.button("Lancer l'analyse automatique IA"):
        with st.spinner("🔎 Analyse en cours..."):
            try:
                analyse = ai_analysis.analyser_scenarios(scenario1, scenario2, results1, results2)
                st.write("**Analyse IA :** " + analyse)
            except Exception as e:
                st.error("Erreur lors de l'appel à l'API d'analyse : " + str(e))
else:
    st.info("⚠️ Pour activer l'analyse automatique, veuillez configurer `openai_api_key` et `openai_base_url` dans `st.secrets`.")
