def COP_variable(T_ext):
    """Calcule le coefficient de performance (COP) du climatiseur en fonction de la température extérieure T_ext (°C)."""
    # On utilise un modèle simple où le COP diminue lorsque la température extérieure augmente.
    # Par exemple: COP ~ 6 à 15°C ext, ~3 à 35°C ext, ~2 à 45°C ext (interpolation linéaire entre ces points).
    if T_ext <= 15.0:
        return 6.0
    elif T_ext < 35.0:
        # Interpolation linéaire de COP entre 15°C (6.0) et 35°C (3.0)
        return 6.0 - (T_ext - 15.0) * (6.0 - 3.0) / (35.0 - 15.0)
    elif T_ext < 45.0:
        # Interpolation linéaire entre 35°C (3.0) et 45°C (2.0)
        return 3.0 - (T_ext - 35.0) * (3.0 - 2.0) / (45.0 - 35.0)
    else:
        # Température extérieure très élevée (>=45°C), COP minimal ~2.0
        return 2.0
