from pydantic import BaseModel, ConfigDict

class ApiRequestBaseModel(BaseModel):
    dashboard_id: int
    api_url: str
    json_payload: str
    mode: str
    code: str
    is_active: bool

class ApiRequestCreateModel(ApiRequestBaseModel):
    pass

class ApiRequestResponseModel(ApiRequestBaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)