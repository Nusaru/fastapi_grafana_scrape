from pydantic import BaseModel, ConfigDict

class GrafanaBaseModel(BaseModel):
    grafana_url: str
    username: str
    password: str
    grafana_code: str

class GrafanaCreateModel(GrafanaBaseModel):
    pass

class GrafanaResponseModel(GrafanaBaseModel):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
