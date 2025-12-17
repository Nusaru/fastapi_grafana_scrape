from pydantic import BaseModel
from typing import Optional

class GrafanaBaseModel(BaseModel):
    grafana_url: str
    username: str
    password: str
    grafana_code: str

class GrafanaCreateModel(GrafanaBaseModel):
    pass

class GrafanaResponseModel(GrafanaBaseModel):
    id: int
    class Config:
        orm_mode = True
