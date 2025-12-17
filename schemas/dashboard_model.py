from pydantic import BaseModel

class DashboardBaseModel(BaseModel):
    dashboard_url: str
    title: str
    grafana_id: int

class DashboardCreateModel(DashboardBaseModel):
    pass

class DashboardResponseModel(DashboardBaseModel):
    id: int
    class Config:
        orm_mode = True
