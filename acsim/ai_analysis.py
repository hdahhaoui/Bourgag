import openai
import streamlit as st

def analyser_scenarios(scenario1, scenario2, results1, results2):
    """
    Utilise l'API OpenAI (DeepSeek) pour générer une analyse automatique des deux scénarios.
    Nécessite `openai_api_key` et `openai_base_url` dans st.secrets.
    """
    # Configuration de l'API OpenAI/DeepSeek
    openai.api_key = st.secrets['openai_api_key']
    openai.api_base = st.secrets['openai_base_url']
    # Préparation du prompt d'analyse en français avec les données des scénarios
    total1 = results1['total_energy_kWh']
    total2 = results2['total_energy_kWh']
    peak1 = results1['peak_power_kW']
    peak2 = results2['peak_power_kW']
    # Description textuelle des scénarios
    description = (
        f"Scénario 1 (baseline) : Isolation {scenario1.isolation}, Vitrage {scenario1.vitrage}, Ventilation {scenario1.ventilation}, Charges internes {scenario1.interne}.\n" 
        f"Consommation annuelle de climatisation : {total1:.1f} kWh, Puissance maximale : {peak1:.1f} kW.\n\n" 
        f"Scénario 2 (optimisé) : Isolation {scenario2.isolation}, Vitrage {scenario2.vitrage}, Ventilation {scenario2.ventilation}, Charges internes {scenario2.interne}.\n" 
        f"Consommation annuelle de climatisation : {total2:.1f} kWh, Puissance maximale : {peak2:.1f} kW.\n\n" 
        "Analyse comparative des deux scénarios :" 
    )
    # Appel à l'API OpenAI pour obtenir l'analyse
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es un assistant expert en efficacité énergétique des bâtiments. Fournis une analyse technique en français."},
            {"role": "user", "content": description}
        ],
        temperature=0.7
    )
    # Récupérer le texte de la réponse de l'assistant
    analyse_text = response['choices'][0]['message']['content'].strip()
    return analyse_text
