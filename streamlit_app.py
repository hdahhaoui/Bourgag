import streamlit as st
import pandas as pd
import altair as alt

from acsim import (
    weather, envelope, ventilation, internal_loads,
    ac_model, thermal_model, scenario, ai_analysis
)

st.set_page_config(page_title="Simulation Climatisation", page_icon="❄️", layout="wide")
st.title("Simulation énergétique d'un climatiseur")

# --------------------------------------------------
# 1. MÉTÉO
# --------------------------------------------------
st.sidebar.header("1. Fichier météo (.EPW)")
epw_file = st.sidebar.file_uploader(
    "Importez votre fichier météo",
    type=["epw"],
    help="Format EnergyPlus Weather : 8760 lignes horaires contenant température, rayonnement, etc."
)
if epw_file is not None:
    meteo_df = weather.read_epw(epw_file)
    st.sidebar.success("Fichier météo importé")
else:
    meteo_df = weather.read_epw("data/exemple_meteo.epw")
    st.sidebar.info("📂 Fichier d'exemple utilisé (exemple_meteo.epw)")

# --------------------------------------------------
# 2. CONSIGNE
# --------------------------------------------------
st.sidebar.header("2. Température intérieure de consigne")
T_int = st.sidebar.number_input(
    "Consigne (°C)",
    min_value=10, max_value=30, value=25,
    help="Température cible que le climatiseur tente de maintenir dans la zone."
)

# --------------------------------------------------
# 3. PARAMÈTRES BÂTIMENT
# --------------------------------------------------
st.sidebar.header("3. Paramètres du bâtiment")

NIVEAUX = ["Faible", "Moyen", "Élevé"]

help_iso  = "Qualité de l'isolation des parois opaques.\nFaible : murs peu isolés (UA ≈ 300 W/K)\nMoyen : isolation standard (UA ≈ 120 W/K)\nÉlevé : RT‑2020 (UA ≈ 100 W/K)"
help_vit  = "Performance des vitrages + protections solaires.\nFaible : simple vitrage, aucun store\nÉlevé : double vitrage performant + stores extérieurs"
help_vent = "Taux de renouvellement d'air (infiltrations + ventilation).\nFaible : 0,2 vol/h — bâtiment très étanche\nÉlevé : 1 vol/h — forte infiltration"
help_int  = "Apports de chaleur internes : occupants, éclairage, appareils.\nFaible ≈ 1,5 kW ; Moyen ≈ 3 kW ; Élevé ≈ 4,5 kW constants."

st.sidebar.subheader("Scénario 1 : Baseline")
iso1  = st.sidebar.selectbox("Isolation", NIVEAUX, index=0, help=help_iso)
vit1  = st.sidebar.selectbox("Vitrage / protections solaires", NIVEAUX, index=0, help=help_vit)
vent1 = st.sidebar.selectbox("Ventilation / infiltrations", NIVEAUX, index=2, help=help_vent)
int1  = st.sidebar.selectbox("Charges internes", NIVEAUX, index=1, help=help_int)

st.sidebar.subheader("Scénario 2 : Optimisé")
iso2  = st.sidebar.selectbox("Isolation ", NIVEAUX, index=2, key="iso2", help=help_iso)
vit2  = st.sidebar.selectbox("Vitrage / protections ", NIVEAUX, index=2, key="vit2", help=help_vit)
vent2 = st.sidebar.selectbox("Ventilation / infiltrations ", NIVEAUX, index=0, key="vent2", help=help_vent)
int2  = st.sidebar.selectbox("Charges internes ", NIVEAUX, index=1, key="int2", help=help_int)

# --------------------------------------------------
# 4. PARAMÈTRES CLIMATISEUR
# --------------------------------------------------
st.sidebar.header("4. Paramètres du climatiseur")

QUALITES_AC = ["Entrée de gamme", "Standard", "Haute efficacité (A+++)"]

type_ac = st.sidebar.selectbox(
    "Type / qualité",
    QUALITES_AC, index=1,
    help="Courbe COP différente :\nEntrée de gamme → COP ~2,5 à 35 °C ext.\nA+++ → COP ~4,3 à 35 °C."
)
cap_nom = st.sidebar.number_input(
    "Puissance nominale (kW froid)",
    1.0, 20.0, 5.0, step=0.5,
    help="Capacité frigorifique maximale de la machine dans les conditions nominales."
)
mod_min = st.sidebar.slider(
    "Modulation minimale (%)",
    10, 100, 30, step=5,
    help="Seuil en dessous duquel l’inverter ne peut plus moduler : la machine cycle -> rendement dégradé."
)

# --------------------------------------------------
# CRÉATION SCÉNARIOS
# --------------------------------------------------
sc1 = scenario.Scenario(iso1, vit1, vent1, int1, T_int, type_ac, cap_nom, mod_min)
sc2 = scenario.Scenario(iso2, vit2, vent2, int2, T_int, type_ac, cap_nom, mod_min)

# --------------------------------------------------
# SIMULATION
# --------------------------------------------------
res1 = thermal_model.simuler_scenario(meteo_df, sc1)
res2 = thermal_model.simuler_scenario(meteo_df, sc2)
df1, df2 = res1["data"], res2["data"]

# --------------------------------------------------
# INDICATEURS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Conso annuelle S1", f"{res1['total_energy_kWh']:.1f} kWh")
col2.metric("Conso annuelle S2", f"{res2['total_energy_kWh']:.1f} kWh")
gain = (1 - res2['total_energy_kWh']/res1['total_energy_kWh'])*100 if res1['total_energy_kWh'] else 0
col3.metric("Économie", f"{gain:.1f} %")

# --------------------------------------------------
# GRAPHIQUES
# --------------------------------------------------
st.subheader("Puissance de refroidissement horaire")
st.altair_chart(thermal_model.creer_graphique_puissance(df1, df2), use_container_width=True)

st.subheader("Énergie cumulée consommée")
st.altair_chart(thermal_model.creer_graphique_energie(df1, df2), use_container_width=True)

st.subheader("Température extérieure et consigne")
st.altair_chart(thermal_model.creer_graphique_temperature(df1, T_int), use_container_width=True)

# --------------------------------------------------
# EXPORT CSV
# --------------------------------------------------
st.download_button(
    "📥 Télécharger les résultats (CSV)",
    thermal_model.exporter_csv(df1, df2),
    file_name="simulation_clim.csv",
    mime="text/csv"
)

# --------------------------------------------------
# ANALYSE IA
# --------------------------------------------------
st.subheader("Analyse automatique IA (DeepSeek)")
if {'openai_api_key', 'openai_base_url'} <= st.secrets.keys():
    if st.button("Lancer l'analyse IA"):
        with st.spinner("Analyse en cours…"):
            commentaire = ai_analysis.analyser_scenarios(sc1, sc2, res1, res2)
            st.markdown(commentaire)
else:
    st.info("Ajoutez `openai_api_key` et `openai_base_url` dans les *Secrets* pour activer l'analyse IA.")
