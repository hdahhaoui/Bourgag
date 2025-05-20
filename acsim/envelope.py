# Paramètres thermiques de l'enveloppe du bâtiment
# Coefficients de transmission thermique (UA en W/K) pour l'isolation des murs/toit en fonction du niveau
UA_wall = {
    "Faible": 300.0,   # Mauvaise isolation -> pertes élevées
    "Moyen": 120.0,    # Isolation moyenne
    "Élevé": 100.0      # Très bonne isolation -> pertes réduites
}
# Coefficients de transmission thermique (UA en W/K) pour les vitrages (fenêtres) en fonction du niveau
UA_window = {
    "Faible": 100.0,   # Simple vitrage, grande surface
    "Moyen": 60.0,     # Vitrage double standard
    "Élevé": 30.0      # Double vitrage performant (faibles pertes)
}
# Facteur solaire effectif (produit du facteur de transmission solaire et de la surface vitrée effective en m2)
# On suppose une surface de fenêtre fixe (20 m2) et un facteur solaire variable selon la qualité du vitrage/protections
WINDOW_AREA = 20.0  # m² de fenêtres (supposé)
g_values = {
    "Faible": 0.8,   # Vitrage peu sélectif, pas de protection solaire (80% du rayonnement transmis)
    "Moyen": 0.6,    # Vitrage standard avec quelques protections (60% transmis)
    "Élevé": 0.4     # Vitrage performant + protections solaires (seulement 40% transmis)
}

def calcul_H_enveloppe(niveau_isolation, niveau_vitrage):
    """Calcule le coefficient global de pertes thermiques par l'enveloppe (W/K) en fonction de l'isolation et du vitrage."""
    H_wall = UA_wall[niveau_isolation]
    H_win = UA_window[niveau_vitrage]
    return H_wall + H_win

def gain_solaire(global_radiation, niveau_vitrage):
    """Calcule le gain de chaleur solaire à travers les vitrages (W) pour un rayonnement global horizontal donné (W/m²)."""
    # Rayonnement global horizontal (global_radiation) multiplié par la surface vitrée et le facteur solaire correspondant
    g = g_values[niveau_vitrage]
    return WINDOW_AREA * g * global_radiation
