import time
import asyncio

from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from crud import CrudGrafana, CrudDashboard, CrudApiRequest
from sqlalchemy.orm import Session
from services.cryptograph import Crypthograph 
from models.db_model import GrafanaModel,GrafanaDashboardModel
from concurrent.futures import ProcessPoolExecutor, as_completed

def processSelenium(listGrafana: List[GrafanaModel]):
    result =[]
    with ProcessPoolExecutor(max_workers=3) as executor:
        for grafana in listGrafana:
            futures = []
            dashboads: List[GrafanaDashboardModel] = grafana.dashboards
            
            for batch in batchingList(dashboads,2):
                scraper = SeleniumScraper(grafana,batch)
                futures.append(
                executor.submit(scraper.dashboardScraping)
                )
        
        for f in as_completed(futures):
            result.append(f.result())

    return result
class SeleniumScraper:
    def __init__(self, grafana: GrafanaModel, batchedDashboard: List[GrafanaDashboardModel]):
        self.grafana = grafana
        self.batchedDashboard = batchedDashboard
        self.cryptograph = Crypthograph()
        self.driver = None

    def dashboardScraping(self):
        option = Options()
        option.add_argument("--headless")
        option.set_preference("app.update.enabled", False)
        option.set_preference("app.update.auto", False)
        option.set_preference("app.update.staging.enabled", False)
        self.driver=webdriver.Firefox(option)

        logginStatus = self.logginGrafana(self.grafana)
        if logginStatus:
            for dashboard in self.batchedDashboard:
                print(dashboard)
        else:
            return "Login Fails"
        return "process Success"
    
    def logginGrafana(self, grafana: GrafanaModel):
        username = grafana.username
        password = self.cryptograph.decrypt(str(grafana.password).encode())
        self.driver.get(str(grafana.grafana_url))

        while True:
            try:
                wait = WebDriverWait(self.driver, 5)
                elementUsername = wait.until(EC.visibility_of_element_located((By.NAME,"user")))
                elementPassword = self.driver.find_element(By.NAME, "password")
                elementLogin = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                elementUsername.send_keys(username)
                elementPassword.send_keys(password)
                elementLogin.click()
                time.sleep(3)
                login=wait.until_not(EC.url_contains("/login"))
                if login==False:
                    break
                else:
                    print("Login failed, retrying...")       
            except Exception as e:
                print(e) 
                return False
        return True

def batchingList(items: List[any], batchSize: int):
    for i in range(0, len(items), batchSize):
        yield items[i: i + batchSize]