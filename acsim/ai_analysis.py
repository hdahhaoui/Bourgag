# acsim/ai_analysis.py
import streamlit as st
from openai import OpenAI   # <- nouveau client
import os

# Création du client OpenAI (API DeepSeek)
client = OpenAI(
    api_key  = st.secrets.get("openai_api_key", os.getenv("OPENAI_API_KEY")),
    base_url = st.secrets.get("openai_base_url", "https://api.deepseek.com/v1")
)

def analyser_scenarios(sc1, sc2, res1, res2):
    """Retourne un commentaire IA (DeepSeek) comparant deux scénarios."""
    conso1 = res1['total_energy_kWh']
    conso2 = res2['total_energy_kWh']
    pct    = (1 - conso2/conso1) * 100 if conso1 else 0

    prompt = (
        "Analyse en français la différence énergétique entre deux scénarios de climatisation :\n"
        f"- Scénario 1 : isolation {sc1.isolation}, vitrage {sc1.vitrage}, ventilation {sc1.ventilation}, "
        f"charges internes {sc1.interne}. Conso annuelle = {conso1:.1f} kWh.\n"
        f"- Scénario 2 : isolation {sc2.isolation}, vitrage {sc2.vitrage}, ventilation {sc2.ventilation}, "
        f"charges internes {sc2.interne}. Conso annuelle = {conso2:.1f} kWh.\n"
        f"Économie : {pct:.1f} %.\n"
        "Explique les raisons techniques de l'écart et donne deux recommandations d'amélioration."
    )

    response = client.chat.completions.create(
        model       = "deepseek-chat",      # ou un autre modèle DeepSeek
        messages    = [{"role": "user", "content": prompt}],
        temperature = 0.7,
        max_tokens  = 300
    )
    return response.choices[0].message.content.strip()
