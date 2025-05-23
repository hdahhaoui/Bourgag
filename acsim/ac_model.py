# Courbes COP (T_ext → COP) pour trois qualités de climatiseur
# Points : (température extérieure en °C, COP)
COP_CURVES = {
    "Entrée de gamme": [(15, 3.0), (25, 2.5), (35, 1.8), (45, 1.5)],
    "Standard":        [(15, 4.2), (25, 3.8), (35, 2.8), (45, 2)],
    "Haute efficacité (A+++)": [(15, 6.5), (25, 5.0), (35, 4.3), (45, 3.0)]
}

def cop_temperature(type_ac: str, T_ext: float) -> float:
    """
    Interpole linéairement le COP en fonction de la température extérieure
    pour le type de climatiseur choisi.
    """
    pts = COP_CURVES[type_ac]
    # Avant la première borne
    if T_ext <= pts[0][0]:
        return pts[0][1]
    # Après la dernière borne
    if T_ext >= pts[-1][0]:
        return pts[-1][1]
    # Interpolation linéaire entre deux points
    for (t1, cop1), (t2, cop2) in zip(pts, pts[1:]):
        if t1 <= T_ext <= t2:
            return cop1 + (cop2 - cop1) * (T_ext - t1) / (t2 - t1)
    # Sécurité :
    return pts[-1][1]
