from sqlalchemy.orm import Session
from models.db_model import GrafanaModel, GrafanaDashboardModel
from schemas.grafana_model import GrafanaCreateModel
from schemas.dashboard_model import DashboardCreateModel

class CrudGrafana:
    def __init__(self, db: Session):
        self.db = db
        
    def insert_grafana(self, grafana_model: GrafanaCreateModel):
        db_grafana = GrafanaModel(
            grafana_url = grafana_model.grafana_url,
            username = grafana_model.username,
            password = grafana_model.password,
            grafana_code = grafana_model.grafana_code
        )
        self.db.add(db_grafana)
        self.db.commit()
        self.db.refresh(db_grafana)
        return db_grafana

    def get_grafana_by_code(self, grafana_code: str):
        return self.db.query(GrafanaModel).filter(GrafanaModel.grafana_code == grafana_code).first()
    
    def get_grafana_by_id(self, id: int):
        return self.db.query(GrafanaModel).filter(GrafanaModel.id == id).first()

class CrudDashboard:
    def __init__(self, db: Session):
        self.db = db
    
    def insert_dashboard(self, dashboard_model: DashboardCreateModel):
        db_dashboard = GrafanaDashboardModel(
            dashboard_url = dashboard_model.dashboard_url,
            title = dashboard_model.title,
            grafana_id = dashboard_model.grafana_id
        )

        self.db.add(db_dashboard)
        self.db.commit()
        self.db.refresh(db_dashboard)

        return db_dashboard
    
    def get_dashboard_by_grafana_id(self, grafana_id: int):
        return self.db.query(GrafanaDashboardModel).filter(GrafanaDashboardModel.grafana_id == grafana_id).all()
    
    def get_dashboard_by_id(self, id: int):
        return self.db.query(GrafanaDashboardModel).filter(GrafanaDashboardModel.id == id).first()
