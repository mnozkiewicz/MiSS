from pydantic import BaseModel
from typing import Any

class AnnealingConfig(BaseModel):
    solution_size: int
    d_max: int
    epochs: int
    steps_per_epoch: int
    initial_temperature: float
    temperature_decay: float
    algorithm: str
    algorithm_params: dict[str, Any]