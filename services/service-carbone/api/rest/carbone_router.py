from fastapi import APIRouter

router = APIRouter(prefix="/carbone", tags=["carbone"])

# TODO: brancher les routes sur les use cases de application/use_cases/
# En cas d'erreur métier, lever une exception de domain/exceptions/exception.py
# (NotFoundException, ValidationException, ...), le container s'occupe du reste.
@router.get("/machines/{machine_id}/events")
def list_events_by_machine(machine_id: str):
    from container import get_carbon_event_repository
    with get_carbon_event_repository() as repository:
        events = repository.find_by_machine(machine_id)
        return[
            {
                "id": e.id,
                "machine_id": e.machine_id,
                "timestamp": e.timestamp,
                "actual_energy_kwh": e.actual_energy_kwh,
                "expected_energy_kwh": e.expected_energy_kwh,
                "wasted_energy_kwh": e.wasted_energy_kwh,
                "avoidable_co2_kg": e.avoidable_co2_kg,
                "status": e.status,
                "probable_cause": e.probable_cause,
            }
            for e in events
        ]

@router.get("/events/{event_id}")
def get_event(event_id: str):
    from container import get_carbon_event_repository
    from domain.exceptions.base_exceptions import NotFoundException

    with get_carbon_event_repository() as repository:
        event = repository.find_by_id(event_id)
        if event is None:
            raise NotFoundException(f"Événement carbone {event_id} introuvable")
        return {
            "id": event.id,
            "machine_id": event.machine_id,
            "timestamp": event.timestamp,
            "actual_energy_kwh": event.actual_energy_kwh,
            "expected_energy_kwh": event.expected_energy_kwh,
            "wasted_energy_kwh": event.wasted_energy_kwh,
            "avoidable_co2_kg": event.avoidable_co2_kg,
            "status": event.status,
            "probable_cause": event.probable_cause,
            "recommendation": event.recommendation,
        }