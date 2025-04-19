import pandas as pd
from acsim import envelope, ventilation, internal_loads, ac_model

def simuler_scenario(weather_df: pd.DataFrame, sc):
    """
    Simulation horaire d'un scénario de bâtiment + climatiseur.
    Retourne un dict avec DataFrame de résultats et indicateurs.
    """
    # Coefficients de pertes
    H_env  = envelope.calcul_H_enveloppe(sc.isolation, sc.vitrage)      # W/K
    H_vent = ventilation.calcul_H_ventilation(sc.ventilation)          # W/K
    Q_int  = internal_loads.charges_internes(sc.interne)               # W
    
    # Params AC
    P_nom  = sc.cap_nom_kW * 1000        # puissance frigorifique nominale (W)
    PLRmin = sc.mod_min_pct / 100        # modulation mini en fraction
    
    # Conteneurs résultats
    P_elec = []
    E_cum  = []
    cum_kWh = 0.0
    
    for _, met in weather_df.iterrows():
        T_ext = met['T_ext']
        ghi   = met['GlobRad']
        
        # Bilan thermique heure
        Q_env  = H_env  * (T_ext - sc.T_int)
        Q_vent = H_vent * (T_ext - sc.T_int)
        Q_sol  = envelope.gain_solaire(ghi, sc.vitrage)
        Q_tot  = Q_env + Q_vent + Q_sol + Q_int          # W
        
        if Q_tot <= 0:
            P_el = 0.0
        else:
            # Calcul Part‑Load Ratio
            PLR = Q_tot / P_nom
            if PLR > 1.0:          # machine saturée → on borne
                PLR = 1.0
            elif PLR < PLRmin:     # cyclage → rendement pénalisé de 20 %
                PLR = PLRmin
            COP = ac_model.cop_temperature(sc.type_ac, T_ext)
            # Option : légère pénalité de COP si PLR<PLRmin
            if Q_tot / P_nom < PLRmin:
                COP *= 0.8
            P_el = (PLR * P_nom) / COP      # W électriques
        P_elec.append(P_el)
        cum_kWh += P_el / 1000.0
        E_cum.append(cum_kWh)
    
    df = pd.DataFrame({
        "datetime": weather_df["datetime"],
        "T_ext":    weather_df["T_ext"],
        "P_kW":     [p/1000 for p in P_elec],
        "E_cum_kWh": E_cum
    })
    return {
        "data": df,
        "total_energy_kWh": cum_kWh,
        "peak_power_kW": max(P_elec)/1000 if P_elec else 0.0
    }

# Les fonctions de graphes et d'export CSV restent inchangées
from altair import Chart, X, Y

def creer_graphique_puissance(df1, df2):
    long_df = pd.concat([
        df1[['datetime', 'P_kW']].assign(Scénario="S1"),
        df2[['datetime', 'P_kW']].assign(Scénario="S2")
    ])
    return Chart(long_df).mark_line().encode(
        x=X('datetime:T', title='Date/Heure'),
        y=Y('P_kW:Q', title='Puissance clim (kW)'),
        color='Scénario:N'
    ).properties(height=300)

def creer_graphique_energie(df1, df2):
    long_df = pd.concat([
        df1[['datetime', 'E_cum_kWh']].assign(Scénario="S1"),
        df2[['datetime', 'E_cum_kWh']].assign(Scénario="S2")
    ])
    return Chart(long_df).mark_line().encode(
        x=X('datetime:T'),
        y=Y('E_cum_kWh:Q', title='Énergie cumulée (kWh)'),
        color='Scénario:N'
    ).properties(height=300)

def creer_graphique_temperature(df, T_int=None):
    base = pd.DataFrame({'datetime': df['datetime'], 'Température': df['T_ext'], 'Type': 'Extérieure'})
    if T_int is not None:
        cons = pd.DataFrame({'datetime': df['datetime'], 'Température': [T_int]*len(df), 'Type': 'Consigne'})
        base = pd.concat([base, cons])
    return Chart(base).mark_line().encode(
        x='datetime:T', y='Température:Q', color='Type:N'
    ).properties(height=300)

def exporter_csv(df1, df2):
    tableau = pd.DataFrame({
        "datetime":            df1['datetime'],
        "T_ext":               df1['T_ext'],
        "Puissance_S1_kW":     df1['P_kW'],
        "Puissance_S2_kW":     df2['P_kW'],
        "Énergie_S1_kWh":      df1['E_cum_kWh'],
        "Énergie_S2_kWh":      df2['E_cum_kWh']
    })
    return tableau.to_csv(index=False).encode("utf-8")
