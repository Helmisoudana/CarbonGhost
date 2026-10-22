# Domaine pur : stdlib uniquement.
from collections import defaultdict, deque
from datetime import datetime
from math import sqrt

from domain.entities.anomaly import Anomaly

FEATURES = ("courant", "temperature", "vibration", "pression")


class AnomalyDetector:
    """
    Détection par z-score glissant, par machine et par capteur.

    Chaque machine garde une fenêtre de ses dernières valeurs NORMALES.
    Une valeur trop éloignée de la moyenne (|z| > seuil) est une anomalie
    et n entre pas dans la fenêtre (évite de polluer la référence).
    Rien n est détecté avant `min_samples` valeurs (démarrage à froid).
    """

    def __init__(self, window_size: int = 60, min_samples: int = 20, z_threshold: float = 3.0):
        self.min_samples = min_samples
        self.z_threshold = z_threshold
        self._windows: dict[tuple[str, str], deque] = defaultdict(lambda: deque(maxlen=window_size))

    def detect(self, machine_id: str, timestamp: datetime, values: dict[str, float]) -> Anomaly | None:
        faulty: dict[str, float] = {}

        for feature in FEATURES:
            value = values[feature]
            window = self._windows[(machine_id, feature)]

            z = self._zscore(window, value)
            if z is not None and abs(z) > self.z_threshold:
                faulty[feature] = abs(z)
            else:
                window.append(value)

        if not faulty:
            return None

        score = max(faulty.values())
        return Anomaly(
            machine_id=machine_id,
            timestamp=timestamp,
            features=sorted(faulty, key=faulty.get, reverse=True),
            score=round(score, 2),
            severity=self._severity(score),
        )

    def _zscore(self, window: deque, value: float) -> float | None:
        n = len(window)
        if n < self.min_samples:
            return None
        mean = sum(window) / n
        std = sqrt(sum((x - mean) ** 2 for x in window) / n)
        std = max(std, 1e-6, abs(mean) * 0.01)  # plancher : évite la division par ~0
        return (value - mean) / std

    def _severity(self, score: float) -> str:
        if score >= self.z_threshold * 2:
            return "critical"
        if score >= self.z_threshold * 1.5:
            return "high"
        return "medium"
