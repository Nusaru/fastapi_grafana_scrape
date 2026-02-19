import os
import sys
import crud
import asyncio
import platform

from crud import CrudGrafana
from scraper.scraper import SeleniumScraper
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from scraper.scraper import SeleniumScraper,processSelenium
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from schemas.grafanaModel import GrafanaCreateModel,GrafanaResponseModel 
from schemas.dashboardModel import DashboardCreateModel,DashboardResponseModel 
from schemas.apiRequestModel import ApiRequestCreateModel, ApiRequestResponseModel 

Base.metadata.create_all(bind=engine)
app = FastAPI()
osName = platform.system()

def getCurrentDirectory(dotEnv: bool =False):
    if osName == "Windows":
        print ("Running OS is Windows")
        if getattr(sys,'frozen',False):
            if dotEnv:
                currentDirectory = getattr(sys, '_MEIPASS',os.path.dirname(sys.executable))
            else:
                currentDirectory = os.path.dirname(sys.executable)  
        else:
            currentDirectory = os.path.dirname(os.path.abspath(sys.argv[0]))
        env_path = os.path.join(currentDirectory,".env")
        load_dotenv(env_path)
    elif osName == "Linux":
        print ("Running OS is Linux")

getCurrentDirectory(True)

@app.get('/')
async def root():
    a=SeleniumScraper()
    return {"message" : a.dashboardScraping() }

#scraper

@app.get('/scraper/triggerScraping')
async def triggerScrapping(db: Session = Depends(get_db)):
    crudGrafana = CrudGrafana(db)
    listGrafanaId = crudGrafana.getAllGrafanaId()
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            processSelenium,
            listGrafanaId
        )
        return result
    except Exception as e:
        return e

# Grafana
@app.post('/grafana/insertGrafana',response_model=GrafanaResponseModel)
async def insertGrafana(grafana_model: GrafanaCreateModel, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.insertGrafana(grafana_model)
    return db_grafana

@app.get('/grafana/{id}')
async def getGrafanaById(id: int, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.getGrafanaById(id)
    return db_grafana

@app.get('/grafana/getByCode/{grafana_code}')
async def getGrafanaByCode(grafana_code: str, db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.getGrafanaByCode(grafana_code)
    return db_grafana

@app.get('/grafana')
async def getGrafanaAll(db: Session = Depends(get_db)):
    crudGrafana = crud.CrudGrafana(db)
    db_grafana = crudGrafana.getAllGrafanaWithDashboardandApi()
    return db_grafana

#Dashboard
@app.post('/dashboard/insertDashboard', response_model=DashboardResponseModel)
async def insertDashboard(dashboard_model: DashboardCreateModel, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.insertDashboard(dashboard_model)
    return db_dashboard

@app.get('/dashboard/{id}')
async def getDashboardByid(id: int, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.getDashboardById(id)
    return db_dashboard

@app.get('/dashboard/getByGrafanaId/{grafana_id}')
async def getDashboardByGrafanaId(grafana_id: int, db: Session = Depends(get_db)):
    crudDashboard = crud.CrudDashboard(db)
    db_dashboard = crudDashboard.getDashboardByGrafanaId(grafana_id)
    return db_dashboard

#request API

@app.post('/apiRequest/insertApiRequest', response_model=ApiRequestResponseModel)
async def insertApiRequest(api_request_model: ApiRequestCreateModel, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.insertApiRequest(api_request_model)
    return db_api_request

@app.get('/apiRequest/{id}')
async def getApiRequestBy(id: int, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.getApiRequestById(id)
    return db_api_request

@app.get('/apiRequest/getByDashboardId/{dashboard_id}')
async def getApiRequestByDashboardId(dashboard_id: int, db: Session = Depends(get_db)):
    crudApiRequest = crud.CrudApiRequest(db)
    db_api_request = crudApiRequest.getApiRequestByDashboardId(dashboard_id)
    return db_api_request
