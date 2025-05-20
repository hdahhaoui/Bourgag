# Charges internes (apports de chaleur internes) en watts selon le niveau
# (incluent par exemple les personnes, éclairages, équipements électriques)
internal_gains = {
    "Faible": 1500.0,    # Faibles apports internes (petite occupation, équipements économes)
    "Moyen": 3000.0,   # Apports moyens
    "Élevé": 4500.0    # Apports élevés (forte occupation, appareils nombreux)
}

def charges_internes(niveau_charges):
    """Retourne la valeur des apports de chaleur internes (W) pour le niveau choisi."""
    return internal_gains[niveau_charges]
