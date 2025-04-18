# Paramètres de ventilation / infiltration d'air
# Taux de renouvellement d'air (volumique) en volume/heure selon le niveau
ACH_values = {
    "Faible": 0.2,   # Bâtiment très étanche (0.2 volumes par heure)
    "Moyen": 0.5,    # Ventilation moyenne (0.5 vol/h)
    "Élevé": 1.0     # Infiltrations élevées (1 vol/h)
}
# Volume intérieur du bâtiment (m³) - hypothèse pour une maison de ~100 m² au sol
VOLUME_M3 = 250.0

def calcul_H_ventilation(niveau_ventilation):
    """Calcule le coefficient de pertes par ventilation/infiltration (W/K) pour le niveau donné."""
    ACH = ACH_values[niveau_ventilation]
    # Formule : H_vent = 0.34 * ACH * Volume, où 0.34 convertit (m3/h) * (J/(m3.K)) en W/K (air ~ 0.34 Wh/m3.K)
    return 0.34 * ACH * VOLUME_M3
