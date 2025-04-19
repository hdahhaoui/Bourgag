class Scenario:
    """
    Regroupe tous les paramètres d'un scénario de simulation.
    """
    def __init__(self,
                 isolation: str,
                 vitrage: str,
                 ventilation: str,
                 interne: str,
                 T_int: float,
                 type_ac: str,
                 cap_nom_kW: float,
                 mod_min_pct: int):
        self.isolation   = isolation      # "Faible" / "Moyen" / "Élevé"
        self.vitrage     = vitrage
        self.ventilation = ventilation
        self.interne     = interne
        self.T_int       = T_int          # °C
        self.type_ac     = type_ac        # "Entrée de gamme" / "Standard" / "Haute efficacité (A+++)"
        self.cap_nom_kW  = cap_nom_kW     # kW froid nominal
        self.mod_min_pct = mod_min_pct    # % minimal de modulation
