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
# SECTION MÉTÉO
# --------------------------------------------------
st.sidebar.header("1. Fichier météo (.EPW)")
epw_file = st.sidebar.file_uploader(
    "Importez votre fichier météo", type=["epw"], help="Format EnergyPlus Weather"
)
if epw_file is not None:
    meteo_df = weather.read_epw(epw_file)
    st.sidebar.success("Fichier météo importé")
else:
    meteo_df = weather.read_epw("data/exemple_meteo.epw")
    st.sidebar.info("📂 Fichier d'exemple utilisé (exemple_meteo.epw)")

# --------------------------------------------------
# SECTION CONSIGNE INTÉRIEURE
# --------------------------------------------------
st.sidebar.header("2. Température intérieure de consigne")
T_int = st.sidebar.number_input("Consigne (°C)", 10, 30, 25)

# --------------------------------------------------
# SECTION PARAMÈTRES BÂTIMENT
# --------------------------------------------------
st.sidebar.header("3. Paramètres du bâtiment")

NIVEAUX = ["Faible", "Moyen", "Élevé"]

st.sidebar.subheader("Scénario 1 : Baseline")
iso1  = st.sidebar.selectbox("Isolation", NIVEAUX, index=0)
vit1  = st.sidebar.selectbox("Vitrage / protections solaires", NIVEAUX, index=0)
vent1 = st.sidebar.selectbox("Ventilation / infiltrations", NIVEAUX, index=2)
int1  = st.sidebar.selectbox("Charges internes", NIVEAUX, index=1)

st.sidebar.subheader("Scénario 2 : Optimisé")
iso2  = st.sidebar.selectbox("Isolation ", NIVEAUX, index=2, key="iso2")
vit2  = st.sidebar.selectbox("Vitrage / protections ", NIVEAUX, index=2, key="vit2")
vent2 = st.sidebar.selectbox("Ventilation / infiltrations ", NIVEAUX, index=0, key="vent2")
int2  = st.sidebar.selectbox("Charges internes ", NIVEAUX, index=1, key="int2")

# --------------------------------------------------
# SECTION PARAMÈTRES CLIMATISEUR
# --------------------------------------------------
st.sidebar.header("4. Paramètres du climatiseur")

QUALITES_AC = ["Entrée de gamme", "Standard", "Haute efficacité (A+++)"]
type_ac = st.sidebar.selectbox("Type / qualité", QUALITES_AC, index=1)
cap_nom = st.sidebar.number_input("Puissance nominale (kW froid)", 1.0, 20.0, 5.0, step=0.5)
mod_min = st.sidebar.slider("Modulation minimale (%)", 10, 100, 30, step=5)

# --------------------------------------------------
# CRÉATION DES SCÉNARIOS
# --------------------------------------------------
sc1 = scenario.Scenario(
    isolation=iso1, vitrage=vit1, ventilation=vent1, interne=int1,
    T_int=T_int, type_ac=type_ac, cap_nom_kW=cap_nom, mod_min_pct=mod_min
)
sc2 = scenario.Scenario(
    isolation=iso2, vitrage=vit2, ventilation=vent2, interne=int2,
    T_int=T_int, type_ac=type_ac, cap_nom_kW=cap_nom, mod_min_pct=mod_min
)

# --------------------------------------------------
# SIMULATION
# --------------------------------------------------
results1 = thermal_model.simuler_scenario(meteo_df, sc1)
results2 = thermal_model.simuler_scenario(meteo_df, sc2)

df1 = results1["data"]
df2 = results2["data"]

# --------------------------------------------------
# INDICATEURS
# --------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Conso annuelle S1", f"{results1['total_energy_kWh']:.1f} kWh")
col2.metric("Conso annuelle S2", f"{results2['total_energy_kWh']:.1f} kWh")
eco = (1 - results2['total_energy_kWh']/results1['total_energy_kWh'])*100 if results1['total_energy_kWh'] else 0
col3.metric("Économie", f"{eco:.1f} %")

# --------------------------------------------------
# GRAPHIQUES
# --------------------------------------------------
st.subheader("Puissance de refroidissement horaire")
st.altair_chart(thermal_model.creer_graphique_puissance(df1, df2), use_container_width=True)

st.subheader("Énergie cumulée consommée")
st.altair_chart(thermal_model.creer_graphique_energie(df1, df2), use_container_width=True)

st.subheader("Température extérieure (et consigne)")
st.altair_chart(thermal_model.creer_graphique_temperature(df1, T_int), use_container_width=True)

# --------------------------------------------------
# TÉLÉCHARGEMENT CSV
# --------------------------------------------------
st.download_button(
    "📥 Télécharger les résultats (CSV)",
    data=thermal_model.exporter_csv(df1, df2),
    file_name="simulation_clim.csv",
    mime="text/csv"
)

# --------------------------------------------------
# ANALYSE IA
# --------------------------------------------------
st.subheader("Analyse automatique IA (DeepSeek)")
if 'openai_api_key' in st.secrets:
    if st.button("Lancer l'analyse IA"):
        with st.spinner("Appel à l'IA en cours…"):
            commentaire = ai_analysis.analyser_scenarios(sc1, sc2, results1, results2)
            st.success("Analyse IA terminée")
            st.markdown(commentaire)
else:
    st.info("Configurez `openai_api_key` et `openai_base_url` dans les *Secrets* pour activer cette fonction.")
