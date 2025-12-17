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
from schemas.api_request_model import ApiRequestCreateModel, ApiRequestResponseModel 

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

@app.get('/grafana/{id}')
def getGrafanaById(id: int, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.get_grafana_by_id(id)
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

@app.get('/dashboard/{id}')
def getDashboardByid(id: int, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.get_dashboard_by_id(id)
    return db_dashboard

@app.get('/dashboard/getByGrafanaId/{grafana_id}')
def getDashboardByGrafanaId(grafana_id: int, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.get_dashboard_by_grafana_id(grafana_id)
    return db_dashboard

#request API

@app.post('/apiRequest/insertApiRequest', response_model=ApiRequestResponseModel)
def insertApiRequest(api_request_model: ApiRequestCreateModel, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.insert_api_request(api_request_model)
    return db_api_request

@app.get('/apiRequest/{id}')
def getApiRequestBy(id: int, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.get_api_request_by_id(id)
    return db_api_request

@app.get('/apiRequest/getByDashboardId/{dashboard_id}')
def getApiRequestByDashboardId(dashboard_id: int, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.get_api_request_by_dashboard_id(dashboard_id)
    return db_api_request
