import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

from infrastructure.adapters.llm.groq_client import GroqAssistantClient
from infrastructure.adapters.kafka.kafka_carbon_event_consumer import (
    KafkaCarbonEventConsumer,
)
from infrastructure.adapters.kafka.kafka_assistant_result_publisher import (
    KafkaAssistantResultPublisher,
)
from infrastructure.adapters.persistence.postgres.carbon_event_repository import (
    PostgresCarbonEventRepository,
)

from application.use_cases.ask_assistant_use_case import AskAssistantUseCase
from application.use_cases.generate_report_use_case import GenerateReportUseCase


class Container:
    def __init__(self):
        # LLM
        self.llm = GroqAssistantClient()

        # Database
        self.engine = create_engine(settings.database_url)
        session_factory = sessionmaker(bind=self.engine)
        self.db_session = session_factory()
        self.repository = PostgresCarbonEventRepository(self.db_session)

        # Use cases
        self.ask_use_case = AskAssistantUseCase(
            self.repository,
            self.llm,
        )

        self.report_use_case = GenerateReportUseCase(
            self.repository,
            self.llm,
        )

        # Kafka
        self.result_publisher = KafkaAssistantResultPublisher(
            broker_address=settings.kafka_broker,
        )
        self.carbon_event_consumer = KafkaCarbonEventConsumer(
            broker_address=settings.kafka_broker,
            group_id="service-assistant",
        )

    def _handle_incoming_event(self, event):
        import asyncio
        explanation = asyncio.run(
            self.ask_use_case.execute(event.machine_id, "Explique cette anomalie detectee.")
        )
        self.result_publisher.publish(event.machine_id, explanation)

    def start_kafka_consumer(self):
        thread = threading.Thread(
            target=self.carbon_event_consumer.consume,
            args=(self._handle_incoming_event,),
            daemon=True,
        )
        thread.start()


container = Container()
