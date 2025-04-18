from acsim import envelope, ventilation, internal_loads, ac_model
import pandas as pd

def simuler_scenario(weather_df, scenario):
    """
    Simule le comportement thermique et le fonctionnement du climatiseur pour un scénario donné.
    Renvoie un dictionnaire avec les données horaires et des indicateurs synthétiques.
    """
    # Paramètres constants du scénario
    T_int = scenario.T_int  # consigne intérieure (°C)
    H_env = envelope.calcul_H_enveloppe(scenario.isolation, scenario.vitrage)  # [W/K] pertes conductives totales par l'enveloppe
    H_vent = ventilation.calcul_H_ventilation(scenario.ventilation)           # [W/K] pertes par ventilation/infiltration
    Q_int = internal_loads.charges_internes(scenario.interne)                 # [W] apports internes constants
    
    # Listes pour stocker les résultats horaires
    P_elec_list = []   # puissance électrique du climatiseur (W) chaque heure
    E_cumul_list = []  # énergie électrique cumulée (kWh) jusqu'à chaque heure
    cumul_kWh = 0.0    # compteur d'énergie cumulée
    
    # Boucle horaire sur le DataFrame météo
    for idx, row in weather_df.iterrows():
        T_ext = row['T_ext']         # Température extérieure actuelle (°C)
        rad = row['GlobRad']         # Rayonnement solaire global horizontal (W/m²)
        # Calcul du bilan thermique de la zone pour cette heure
        Q_env = H_env * (T_ext - T_int)    # pertes/gains par l'enveloppe (W)
        Q_vent = H_vent * (T_ext - T_int)  # pertes/gains par renouvellement d'air (W)
        Q_solar = envelope.gain_solaire(rad, scenario.vitrage)  # gains solaires à travers les fenêtres (W)
        # Somme des apports thermiques nets sur l'heure (W)
        Q_total = Q_env + Q_vent + Q_int + Q_solar
        # Si Q_total est positif, c'est un gain de chaleur intérieur (besoin de refroidissement);
        # si négatif, c'est une perte de chaleur (aucun besoin de climatisation, on néglige le chauffage ici).
        if Q_total <= 0:
            # Pas de besoin de refroidissement
            P_elec = 0.0
        else:
            # Refroidissement nécessaire: calcul de la puissance du climatiseur
            COP = ac_model.COP_variable(T_ext)
            # Puissance électrique consommée = puissance de refroidissement requise / COP
            P_elec = Q_total / COP
        # Mettre en mémoire la puissance (W) consommée cette heure
        P_elec_list.append(P_elec)
        # Calcul de l'énergie cumulée (kWh) jusqu'à cette heure
        cumul_kWh += P_elec / 1000.0  # convertir W en kW et intégrer sur 1h
        E_cumul_list.append(cumul_kWh)
    
    # Calcul des indicateurs de performance
    total_energy_kWh = E_cumul_list[-1] if E_cumul_list else 0.0
    peak_power_W = max(P_elec_list) if P_elec_list else 0.0
    
    # Construction du DataFrame de résultats horaires pour ce scénario
    result_df = pd.DataFrame({
        'datetime': weather_df['datetime'],
        'T_ext': weather_df['T_ext'],
        'P_kW': [p/1000.0 for p in P_elec_list],
        'E_cum_kWh': E_cumul_list
    })
    return {
        'data': result_df,
        'total_energy_kWh': total_energy_kWh,
        'peak_power_kW': peak_power_W / 1000.0
    }

def creer_graphique_puissance(df1, df2):
    """Crée un graphique Altair comparant la puissance de refroidissement horaire (kW) des deux scénarios."""
    import altair as alt
    # Préparation des données en format long pour Altair
    data1 = df1[['datetime', 'P_kW']].copy()
    data1['Scénario'] = "Scénario 1"
    data2 = df2[['datetime', 'P_kW']].copy()
    data2['Scénario'] = "Scénario 2"
    combined = pd.concat([data1, data2])
    # Création du graphique à lignes
    chart = alt.Chart(combined).mark_line().encode(
        x=alt.X('datetime:T', title='Date/Heure'),
        y=alt.Y('P_kW:Q', title='Puissance de refroidissement (kW)'),
        color='Scénario:N'
    ).properties(height=300)
    return chart

def creer_graphique_energie(df1, df2):
    """Crée un graphique Altair comparant l'énergie électrique cumulée (kWh) des deux scénarios."""
    import altair as alt
    data1 = df1[['datetime', 'E_cum_kWh']].copy()
    data1['Scénario'] = "Scénario 1"
    data2 = df2[['datetime', 'E_cum_kWh']].copy()
    data2['Scénario'] = "Scénario 2"
    combined = pd.concat([data1, data2])
    chart = alt.Chart(combined).mark_line().encode(
        x=alt.X('datetime:T', title='Date/Heure'),
        y=alt.Y('E_cum_kWh:Q', title='Énergie cumulée (kWh)'),
        color='Scénario:N'
    ).properties(height=300)
    return chart

def creer_graphique_temperature(df, T_int=None):
    """Crée un graphique Altair montrant la température extérieure (et la température intérieure de consigne si fournie)."""
    import altair as alt
    data_ext = pd.DataFrame({'datetime': df['datetime'], 'Temp': df['T_ext']})
    data_ext['Type'] = "Température extérieure"
    data_combined = data_ext.copy()
    if T_int is not None:
        # Ajouter une série constante pour la température intérieure de consigne
        data_int = pd.DataFrame({'datetime': df['datetime'], 'Temp': [T_int]*len(df)})
        data_int['Type'] = "Température intérieure (consigne)"
        data_combined = pd.concat([data_ext, data_int])
    chart = alt.Chart(data_combined).mark_line().encode(
        x=alt.X('datetime:T', title='Date/Heure'),
        y=alt.Y('Temp:Q', title='Température (°C)'),
        color='Type:N'
    ).properties(height=300)
    return chart

def exporter_csv(df1, df2):
    """Exporte les résultats des deux scénarios dans un seul tableau CSV (au format texte)."""
    # Combiner les données pertinentes des deux scénarios
    combined = pd.DataFrame({
        "Date/Heure": df1['datetime'],
        "Température extérieure (°C)": df1['T_ext'],
        "Puissance Scénario 1 (kW)": df1['P_kW'],
        "Puissance Scénario 2 (kW)": df2['P_kW'],
        "Énergie cumulée Scénario 1 (kWh)": df1['E_cum_kWh'],
        "Énergie cumulée Scénario 2 (kWh)": df2['E_cum_kWh']
    })
    # Conversion du DataFrame en CSV (chaîne de caractères)
    csv_data = combined.to_csv(index=False, sep=',', encoding='utf-8')
    return csv_data
