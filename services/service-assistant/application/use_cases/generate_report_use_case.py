from datetime import datetime, timedelta

from domain.ports.repositories.i_carbon_event_repository import (
    ICarbonEventRepository
)
from infrastructure.adapters.llm.groq_client import GroqAssistantClient


class GenerateReportUseCase:
    def __init__(
        self,
        repository: ICarbonEventRepository,
        llm: GroqAssistantClient,
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
Tu es un assistant specialise dans le monitoring
energetique et carbone d'un batiment intelligent.
Genere un rapport professionnel en francais.
Le rapport doit contenir :
1. Resume general
2. Nombre d'evenements
3. Machines concernees
4. Evenements importants
5. Temps de recuperation
6. Recommandations
Ne cree aucune donnee qui n'existe pas.
"""

        user_prompt = f"""
Periode analysee :
De {start}
A {end}

Donnees :
{context}
"""

        return await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def _build_context(self, events):
        if not events:
            return "Aucun evenement durant cette periode."
        return "\n".join(
            [
                f"""
    Machine : {event.machine_id}
    Date : {event.timestamp}
    Energie reelle : {event.actual_energy_kwh} kWh
    Energie attendue : {event.expected_energy_kwh} kWh
    Surconsommation : {event.surconsommation_pct}%
    CO2 evitable : {event.avoidable_co2_kg} kg
    Cause probable : {event.probable_cause}
    Recommandation : {event.recommendation}
    """
                for event in events
            ]
        )
