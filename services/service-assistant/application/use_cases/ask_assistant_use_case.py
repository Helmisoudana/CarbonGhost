from domain.safety_policy import SafetyPolicy
from domain.exceptions.domain_exceptions import UnsafeResponseException
from application.prompts.assistant_prompts import SYSTEM_PROMPT, build_ask_prompt


class AskAssistantUseCase:
    def __init__(self, repository, llm_client):
        self.repository = repository
        self.llm_client = llm_client

    async def execute(self, machine_id: str, question: str) -> str:
        SafetyPolicy.validate_question(question)
        context = self.repository.get_context_for_llm(machine_id)
        prompt = build_ask_prompt(question, context)
        response = await self.llm_client.generate(system_prompt=SYSTEM_PROMPT, user_prompt=prompt)
        SafetyPolicy.validate_response(response)
        return response