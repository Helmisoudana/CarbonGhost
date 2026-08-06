from pydantic import BaseModel
from datetime import datetime

class EnergyPrediction(BaseModel):
    machine_id: str
    timestamp: datetime
    quantite_produite: int
    temperature: float
    pression: float
    vitesse_moteur: float
    duree_fonctionnement:float
    type_produit: str
    heure: int
    etat_machine:str
    energie_attendue_kwh: float
    
