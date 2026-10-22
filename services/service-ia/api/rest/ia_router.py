from fastapi import APIRouter

router = APIRouter(prefix="/ia", tags=["ia"])


def _dto(a):
    return {
        "id": a.id,
        "machine_id": a.machine_id,
        "timestamp": a.timestamp,
        "features": a.features,
        "score": a.score,
        "severity": a.severity,
    }


@router.get("/machines/{machine_id}/anomalies")
def list_anomalies_by_machine(machine_id: str):
    from container import get_anomaly_repository
    with get_anomaly_repository() as repository:
        return [_dto(a) for a in repository.find_by_machine(machine_id)]


@router.get("/anomalies/{anomaly_id}")
def get_anomaly(anomaly_id: str):
    from container import get_anomaly_repository
    from domain.exceptions.base_exceptions import NotFoundException

    with get_anomaly_repository() as repository:
        anomaly = repository.find_by_id(anomaly_id)
        if anomaly is None:
            raise NotFoundException(f"Anomalie {anomaly_id} introuvable")
        return _dto(anomaly)
