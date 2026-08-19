from datetime import datetime
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from domain.entities.carbon_event import CarbonEvent
from domain.ports.repositories.i_carbon_event_repository import (
    ICarbonEventRepository
)


class CarbonEventRepository(ICarbonEventRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_recent_events(self, limit: int = 20) -> List[CarbonEvent]:

        query = text("""
            SELECT
                id, machine_id, timestamp,
                actual_energy_kwh, expected_energy_kwh,
                surconsommation_pct, avoidable_co2_kg,
                probable_cause, confidence, recommendation
            FROM carbon_ghost_events
            ORDER BY timestamp DESC
            LIMIT :limit
        """)

        result = self.db.execute(query, {"limit": limit})

        return [self._map_row(row) for row in result]

    def get_events_between(self, start: datetime, end: datetime) -> List[CarbonEvent]:

        query = text("""
            SELECT
                id, machine_id, timestamp,
                actual_energy_kwh, expected_energy_kwh,
                surconsommation_pct, avoidable_co2_kg,
                probable_cause, confidence, recommendation
            FROM carbon_ghost_events
            WHERE timestamp BETWEEN :start AND :end
            ORDER BY timestamp DESC
        """)

        result = self.db.execute(query, {"start": start, "end": end})

        return [self._map_row(row) for row in result]

    def get_events_by_machine(self, machine_id: str, limit: int = 20) -> List[CarbonEvent]:

        query = text("""
            SELECT
                id, machine_id, timestamp,
                actual_energy_kwh, expected_energy_kwh,
                surconsommation_pct, avoidable_co2_kg,
                probable_cause, confidence, recommendation
            FROM carbon_ghost_events
            WHERE machine_id = :machine_id
            ORDER BY timestamp DESC
            LIMIT :limit
        """)

        result = self.db.execute(query, {"machine_id": machine_id, "limit": limit})

        return [self._map_row(row) for row in result]

    def _map_row(self, row) -> CarbonEvent:
        return CarbonEvent(
            id=row.id,
            machine_id=row.machine_id,
            timestamp=row.timestamp,
            actual_energy_kwh=row.actual_energy_kwh,
            expected_energy_kwh=row.expected_energy_kwh,
            surconsommation_pct=row.surconsommation_pct,
            avoidable_co2_kg=row.avoidable_co2_kg,
            probable_cause=row.probable_cause,
            confidence=row.confidence,
            recommendation=row.recommendation,
        )