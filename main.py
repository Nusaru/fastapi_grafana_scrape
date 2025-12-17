import os
import sys
import crud
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from scraper.scraper import SeleniumScraper
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas.grafana_model import GrafanaCreateModel,GrafanaResponseModel 
from schemas.dashboard_model import DashboardCreateModel,DashboardResponseModel 

Base.metadata.create_all(bind=engine)
app = FastAPI()

def getCurrentDirectory(self, dotEnv: bool =False):
        if getattr(sys,'frozen',False):
            if dotEnv:
                return getattr(sys, '_MEIPASS',os.path.dirname(sys.executable))
            else:
                return os.path.dirname(sys.executable)  
        else:
            return os.path.dirname(os.path.abspath(sys.argv[0]))

env_path = os.path.join(getCurrentDirectory(True),".env")
load_dotenv(env_path)

@app.get('/')
async def root():
    a=SeleniumScraper()
    return {"message" : a.getDashboard() }

# Grafana
@app.post('/grafana/insertGrafana',response_model=GrafanaResponseModel)
def insertGrafana(grafana_model: GrafanaCreateModel, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.insert_grafana(grafana_model)
    return db_grafana

@app.get('/grafana/getByCode/{grafana_code}')
def getGrafanaByCode(grafana_code: str, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.get_grafana_by_code(grafana_code)
    return db_grafana

#Dashboard
@app.post('/dashboard/insertDashboard', response_model=DashboardResponseModel)
def insertDashboard(dashboard_model: DashboardCreateModel, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.insert_dashboard(dashboard_model)
    return db_dashboard

@app.get('/dashboard/getByGrafanaId/{grafana_id}')
def getByGrafanaId(grafana_id: str, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_grafana = crudDashboard.get_dashboard_by_grafana_id(grafana_id)
    return db_grafana
