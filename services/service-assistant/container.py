from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from infrastructure.persistence.postgres.carbon_event_repository import CarbonEventRepository
from infrastructure.llm.groq_client import GroqClient
from application.use_cases.ask_assistant_use_case import AskAssistantUseCase
from application.use_cases.generate_report_use_case import GenerateReportUseCase


class Container:
    """
    Conteneur central des dépendances du service Assistant.
    """

    def __init__(self):

        # --- LLM ---
        self.llm = GroqClient()

        # --- Base de données ---
        self.engine = create_engine(settings.database_url)
        session_factory = sessionmaker(bind=self.engine)
        self.db_session = session_factory()

        # --- Repository ---
        self.repository = CarbonEventRepository(self.db_session)

        # --- Use Cases ---
        self.ask_use_case = AskAssistantUseCase(self.repository, self.llm)
        self.report_use_case = GenerateReportUseCase(self.repository, self.llm)


container = Container()