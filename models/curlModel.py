from pydantic import BaseModel

class VmResultModel(BaseModel):
    metrics: MetricsModel
    values: list[list]

class MetricsModel(BaseModel):
    instance:str
    job:str
    volume:str
