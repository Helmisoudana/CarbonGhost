# domain/services/energy_estimator.py — AUCUN import externe
"""
C'est ici que vit l'hypothèse métier la plus importante du service, donc
la plus discutable : comment transforme-t-on un "courant" (A) capteur en
kWh, et comment définit-on l'énergie "attendue" pour une production
donnée ?

Pour le MVP, avant que service-ia ne fournisse de vraies prédictions
(cf. shared/contracts/energy_prediction.py), on utilise un modèle
linéaire simple, volontairement isolé ici pour être remplacé facilement
plus tard sans toucher au use case ni à l'infrastructure :

    actual_energy_kwh   = courant(A) * tension(V) * cos(phi) * durée(h) / 1000
    expected_energy_kwh = production_count * kwh_attendu_par_unité

Toutes les constantes physiques sont injectées au constructeur (donc
configurables via les variables d'environnement du container), jamais
codées en dur ici.
"""
from dataclasses import dataclass


@dataclass
class EnergyEstimator:
    voltage: float               # tension nominale, en volts (ex: 230)
    power_factor: float          # cos(phi), entre 0 et 1
    sampling_interval_hours: float  # durée représentée par une mesure (ex: 1/60 pour une mesure/minute)
    expected_kwh_per_unit: float  # énergie attendue par unité produite (baseline machine)

    def estimate_actual_energy_kwh(self, courant: float) -> float:
        if courant < 0:
            raise ValueError("courant ne peut pas être négatif")
        return (courant * self.voltage * self.power_factor * self.sampling_interval_hours) / 1000

    def estimate_expected_energy_kwh(self, production_count: int) -> float:
        if production_count < 0:
            raise ValueError("production_count ne peut pas être négatif")
        return production_count * self.expected_kwh_per_unit
