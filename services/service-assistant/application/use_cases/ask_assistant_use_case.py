from typing import List

from domain.entities.carbon_event import CarbonEvent
from domain.ports.repositories.i_carbon_event_repository import (
    ICarbonEventRepository
)
from domain.safety_policy import SafetyPolicy

from infrastructure.llm.groq_client import GroqClient


class AskAssistantUseCase:

    def __init__(
        self,
        repository: ICarbonEventRepository,
        llm: GroqClient,
    ):
        self.repository = repository
        self.llm = llm

    async def execute(
        self,
        question: str
    ) -> str:

        # 1. Vérification sécurité
        SafetyPolicy.validate_question(question)

        # 2. Récupération des données
        events = self.repository.get_recent_events(
            limit=20
        )

        # 3. Transformation des données
        context = self._build_context(events)

        # 4. Prompt système
        system_prompt = """
Tu es l'assistant intelligent d'un système
de monitoring énergétique et carbone.

Tu dois répondre uniquement à partir des données
fournies dans le contexte.

Ne fabrique jamais de données.

Si les données ne permettent pas de répondre,
indique clairement que l'information n'est pas disponible.

Réponds en français de manière claire et concise.
"""

        # 5. Question utilisateur
        user_prompt = f"""
CONTEXTE DES ÉVÉNEMENTS :

{context}

QUESTION :

{question}
"""

        # 6. Appel LLM
        response = await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return response

    def _build_context(self, events: List[CarbonEvent]) -> str:

        if not events:
            return "Aucun événement carbone récent."

        lines = []

        for event in events:
            lines.append(
                f"""
    Événement #{event.id}
    Machine : {event.machine_id}
    Date : {event.timestamp}
    Énergie réelle : {event.actual_energy_kwh} kWh
    Énergie attendue : {event.expected_energy_kwh} kWh
    Surconsommation : {event.surconsommation_pct}%
    CO2 évitable : {event.avoidable_co2_kg} kg
    Cause probable : {event.probable_cause}
    Confiance : {event.confidence}%
    Recommandation : {event.recommendation}
    """
            )

        return "\n".join(lines)