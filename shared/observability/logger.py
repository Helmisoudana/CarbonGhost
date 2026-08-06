import logging
import json
from datetime import datetime

def get_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def log_json(level: str, message: str, trace_id: str = None, machine_id: str = None, **extra):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service_name": service_name,
            "level": level,
            "message": message,
            "trace_id": trace_id,
            "machine_id": machine_id,
            "extra": extra or None,
        }
        logger.log(getattr(logging, level), json.dumps(entry))

    return log_json