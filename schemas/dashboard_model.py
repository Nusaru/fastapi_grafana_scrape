from pydantic import BaseModel, ConfigDict

class DashboardBaseModel(BaseModel):
    dashboard_url: str
    title: str
    grafana_id: int

class DashboardCreateModel(DashboardBaseModel):
    pass

class DashboardResponseModel(DashboardBaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)