from groq import AsyncGroq

from config import settings


class GroqClient:

    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.groq_api_key
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:

        response = await self.client.chat.completions.create(
            model=settings.groq_model,
            temperature=0.2,
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return response.choices[0].message.content or ""