import time
import json
import asyncio
import crud
import platform

from urllib.parse import urlencode, urlparse,parse_qs
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service

from services.curlServices import getRangeSixHours, CurlScraping
from services.cryptograph import Crypthograph 
from services.telegramServices import TelegramFunction
from models.dbModel import GrafanaModel,GrafanaDashboardModel,ApiRequestModel
from concurrent.futures import ProcessPoolExecutor, as_completed
from constant.constant import CaptionBuilder, grafanaHomeTitle, grafanaTitle
from database import get_db_ctx

def processSelenium(listGrafanaId: List[int]):
    result =[]
    with get_db_ctx() as localDb: 
        crudDashBoard = crud.CrudDashboard(localDb)
        with ProcessPoolExecutor(max_workers=3) as executor:
            for grafanaId in listGrafanaId:
                futures = []
                listDasboardId = crudDashBoard.getAllDasbhoardIdByGrafanaId(grafanaId)
                batches = batchingList(listDasboardId,2)
                for batch in batches:
                    scraper = SeleniumScraper(grafanaId,batch)
                    futures.append(
                        executor.submit(scraper.initWebDriver)
                    )
            
            for f in as_completed(futures):
                result.append(f.result())
    scraper.driverExit()
    return result
class SeleniumScraper:
    def __init__(self, grafanaId: int, listDashboardId: List[int]):
        self.listDashboard: List[GrafanaDashboardModel] = []
        self.listApiReq: List[ApiRequestModel] = []
        with get_db_ctx() as localDb:
            crudGrafana = crud.CrudGrafana(localDb)
            crudDashboard = crud.CrudDashboard(localDb)
            self.grafana = crudGrafana.getGrafanaById(grafanaId)
            for dashboardId in listDashboardId:
                dashboard = crudDashboard.getDashboardById(dashboardId)
                self.listDashboard.append(dashboard)

        self.cryptograph = Crypthograph()
        self.driver = None
        self.captionBuilder = CaptionBuilder()
        self.telegramFunction = TelegramFunction()
        self.osName = platform.system()

    def initWebDriver(self):
        option = Options()
        option.add_argument("--headless")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-shm-usage")
        option.set_preference("app.update.enabled", False)
        option.set_preference("app.update.auto", False)
        option.set_preference("app.update.staging.enabled", False)
        
        if self.osName == "Windows":
            self.driver=webdriver.Firefox(options=option)
        else:
            self.driver = webdriver.Firefox(options=option)
        self.driver.command_executor.set_timeout(300)

        return self.dashboardScraping()

    def dashboardScraping(self):
        listResponse=[]
        logginStatus = self.logginGrafana(self.grafana)
        if logginStatus:
            for dashboard in self.listDashboard:
                caption=""
                print("Scraping dashboard ",dashboard.title)

                with get_db_ctx() as localDb:
                    crudApiReq = crud.CrudApiRequest(localDb)
                    self.listApiReq = crudApiReq.getApiRequestByDashboardId(dashboard.id)
                
                for apiReq in self.listApiReq:
                    timeNow = getRangeSixHours()["now"]
                    pastSixHour = getRangeSixHours()["pastSixHour"]
                    curlScraping = CurlScraping(self.grafana.username,self.grafana.password)
                    jsonPayload = json.loads(apiReq.json_payload)
                    dsType = getDsType(apiReq.api_url)
                    
                    if apiReq.mode=='form':
                        jsonPayload['start']=int(timeNow)
                        jsonPayload['end']=int(pastSixHour)
                        payload = urlencode(jsonPayload)
                    else:
                        if dsType == "mssql":
                            jsonPayload['from']=str(int(timeNow))                      
                            jsonPayload['to']=str(int(timeNow)+50)
                        else:
                            nowMs = int(int(timeNow) * 1000)
                            jsonPayload['from']=str(nowMs)                      
                            jsonPayload['to']=str(nowMs+50)
                        payload = json.dumps(jsonPayload)
                    
                    while True:
                        raw = json.loads(curlScraping.postPyCurl(apiReq.api_url,payload,apiReq.mode)) 
                        if raw != {} or not None:
                            break
                    parsed = curlScraping.parse(raw)
                    caption += self.captionBuilder.buildTelegramCaptionByCode(parsed,apiReq.code)
                    if len(self.listApiReq) > 1:
                        caption += "\n-------------------\n"

                    listResponse.append(parsed)

                strFileName = self.getPageScreenshot(dashboard)
                asyncio.run(self.telegramFunction.sendImageWithCaption(strFileName))
                asyncio.run(self.telegramFunction.sendText(caption))
        else:
            print("Login Failed, Retrying...")
            self.dashboardScraping()
        return listResponse
    
    def getPageScreenshot(self, dashboard: GrafanaDashboardModel):
        loadCompleted: bool = False
        title = ""
        try:
            self.driver.get(dashboard.dashboard_url)
            loadCompleted = self.pageIsFullyLoaded()
            title = self.driver.title
            if loadCompleted == False or (title == grafanaHomeTitle or title == grafanaTitle):
                self.getPageScreenshot(dashboard)
        except Exception as e:
            print(e)

        time.sleep(3)
        self.driver.set_window_size(1920, 500)
        scroll_height = self.driver.execute_script(
        "return document.querySelector('.main-view').scrollHeight"
        )

        self.driver.set_window_size(1920, scroll_height)

        if loadCompleted == False or (title == grafanaHomeTitle or title == grafanaTitle):
            self.getPageScreenshot(dashboard)

        try:
            wait = WebDriverWait(self.driver,2)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"[aria-label='Undock menu']")))
            elementDock = self.driver.find_element(By.CSS_SELECTOR,"[aria-label='Undock menu']")
            elementDock.click()
        except:
            print("No Side Panel Found")
        
        self.waitPanelLoading()
        
        strFileName= "./resource/"+ dashboard.filename + ".png"
        
        print(f"saving screenshot to {strFileName}")
        self.driver.save_full_page_screenshot(strFileName)

        return strFileName

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

    def waitPanelLoading(self):
        maxRetries = 5
        for attempt in range(maxRetries):
            start_time= time.time()
            timeout=300
            self.driver.execute_script("""
                const mid = document.body.scrollHeight / 2;
                window.scrollTo(0, mid);
            """)

            time.sleep(0.5) 
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5) 

            self.driver.execute_script("window.scrollTo(0, 0)")

            while True:
                loading_bars = self.driver.find_elements(By.CSS_SELECTOR, "[aria-label='Panel loading bar']")
                print(f"loading bar count = {len(loading_bars)}")
                if len(loading_bars) == 0:
                    return
                
                if time.time() - start_time > timeout:
                    print(f"Timeout Reached. Retrying {attempt+1}/{maxRetries}")
                    break

                time.sleep(0.5)
        raise TimeoutError(f"Panel loading did not finish after {maxRetries} attempts")
    
    def pageIsFullyLoaded(self):
        wait = WebDriverWait(self.driver,30)
        return wait.until(lambda driver: self.driver.execute_script("return document.readyState") == "complete")

    def driverExit(self):
        self.driver.quit()     

def batchingList(items: List[any], batchSize: int):
    for i in range(0, len(items), batchSize):
        yield items[i: i + batchSize]

def getDsType(url: str):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    return qs.get('ds_type',[None])[0]