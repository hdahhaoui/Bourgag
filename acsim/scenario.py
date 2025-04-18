class Scenario:
    """Classe regroupant les paramètres d'un scénario de simulation."""
    def __init__(self, isolation, vitrage, ventilation, interne, T_int):
        self.isolation = isolation      # niveau d'isolation de l'enveloppe (string: "Faible", "Moyen", "Élevé")
        self.vitrage = vitrage          # niveau de performance des vitrages/protections solaires (string)
        self.ventilation = ventilation  # niveau d'infiltration/ventilation (string)
        self.interne = interne          # niveau des charges internes (string)
        self.T_int = T_int              # température intérieure de consigne (°C)
