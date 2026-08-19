from datetime import datetime, timedelta

from domain.ports.repositories.i_carbon_event_repository import (
    ICarbonEventRepository
)

from infrastructure.llm.groq_client import GroqClient


class GenerateReportUseCase:

    def __init__(
        self,
        repository: ICarbonEventRepository,
        llm: GroqClient,
    ):
        self.repository = repository
        self.llm = llm

    async def execute(
        self,
        hours: int = 24
    ) -> str:

        end = datetime.utcnow()
        start = end - timedelta(hours=hours)

        events = self.repository.get_events_between(
            start=start,
            end=end,
        )

        context = self._build_context(events)

        system_prompt = """
Tu es un assistant spécialisé dans le monitoring
énergétique et carbone d'un bâtiment intelligent.

Génère un rapport professionnel en français.

Le rapport doit contenir :

1. Résumé général
2. Nombre d'événements
3. Machines concernées
4. Événements importants
5. Temps de récupération
6. Recommandations

Ne crée aucune donnée qui n'existe pas.
"""

        user_prompt = f"""
Période analysée :

De {start}
À {end}

Données :

{context}
"""

        return await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _build_context(self, events):

        if not events:
            return "Aucun événement durant cette période."

        return "\n".join(
            [
                f"""
    Machine : {event.machine_id}
    Date : {event.timestamp}
    Énergie réelle : {event.actual_energy_kwh} kWh
    Énergie attendue : {event.expected_energy_kwh} kWh
    Surconsommation : {event.surconsommation_pct}%
    CO2 évitable : {event.avoidable_co2_kg} kg
    Cause probable : {event.probable_cause}
    Recommandation : {event.recommendation}
    """
                for event in events
            ]
        )