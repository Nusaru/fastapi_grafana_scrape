import time
import json
import asyncio

from urllib.parse import urlencode
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from services.curlServices import getRangeSixHours, CurlScraping
from services.cryptograph import Crypthograph 
from services.telegramServices import TelegramFunction
from models.dbModel import GrafanaModel,GrafanaDashboardModel,ApiRequestModel
from concurrent.futures import ProcessPoolExecutor, as_completed
from constant.constant import CaptionBuilder, grafanaHomeTitle

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
    def __init__(self, grafana: GrafanaModel, listDashboard: List[GrafanaDashboardModel]):
        self.grafana = grafana
        self.listDashboard = listDashboard
        self.cryptograph = Crypthograph()
        self.driver = None
        self.captionBuilder = CaptionBuilder()
        self.telegramFunction = TelegramFunction()

    def dashboardScraping(self):
        listResponse=[]
        option = Options()
        option.add_argument("--headless")
        option.set_preference("app.update.enabled", False)
        option.set_preference("app.update.auto", False)
        option.set_preference("app.update.staging.enabled", False)
        self.driver=webdriver.Firefox(option)

        logginStatus = self.logginGrafana(self.grafana)
        if logginStatus:
            for dashboard in self.listDashboard:
                caption=""
                listApiReq:List[ApiRequestModel] = dashboard.api_request
                for apiReq in listApiReq:
                    timeNow = getRangeSixHours()["now"]
                    pastSixHour = getRangeSixHours()["pastSixHour"]
                    curlScraping = CurlScraping(self.grafana.username,self.grafana.password)
                    jsonPayload = json.loads(apiReq.json_payload)
                    
                    if apiReq.mode=='form':
                        jsonPayload['start']=int(timeNow)
                        jsonPayload['end']=int(pastSixHour)
                        payload = urlencode(jsonPayload)
                    else:
                        jsonPayload['from']=str(int(timeNow))                      
                        jsonPayload['to']=str(int(timeNow)+50)
                        payload = json.dumps(jsonPayload)
                    
                    while True:
                        raw = json.loads(curlScraping.postPyCurl(apiReq.api_url,payload,apiReq.mode)) 
                        print(json.dumps(raw,indent=2))
                        if raw != {} or not None:
                            break
                    parsed = curlScraping.parse(raw)
                    caption += self.captionBuilder.buildTelegramCaptionByCode(parsed,apiReq.code)

                    listResponse.append(parsed)

                strFileName = self.getPageScreenshot(dashboard)
                asyncio.run(self.telegramFunction.sendImageWithCaption(strFileName))
                asyncio.run(self.telegramFunction.sendText(caption))
                print(dashboard.title)
        else:
            return "Login Fails"
        return listResponse
    
    def getPageScreenshot(self, dashboard: GrafanaDashboardModel):
        try:
            while True:
                self.driver.get(dashboard.dashboard_url)
                wait = WebDriverWait(self.driver,5)
                loadCompleted = wait.until(EC.url_contains(dashboard.dashboard_url))
                tittle = self.driver.title
                if loadCompleted == True and tittle != grafanaHomeTitle:
                    break
        except Exception as e:
            print(e)

        print(f'title = {self.driver.title}')
        time.sleep(3)
        self.driver.set_window_size(1920, 500)
        scroll_height = self.driver.execute_script(
        "return document.querySelector('.main-view').scrollHeight"
        )

        self.driver.set_window_size(1920, scroll_height)

        try:
            wait = WebDriverWait(self.driver,2)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"[aria-label='Undock menu']")))
            elementDock = self.driver.find_element(By.CSS_SELECTOR,"[aria-label='Undock menu']")
            elementDock.click()
        except:
            print("No Side Panel Found")
        
        self.waitPanelLoading()
        
        strFileName= "./resource/"+ dashboard.filename + ".png"
        
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
        start_time= time.time()
        timeout=120
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
            if len(loading_bars) == 0:
                return True
            
            if time.time() - start_time > timeout:
                return False

            time.sleep(0.5)
        
def batchingList(items: List[any], batchSize: int):
    for i in range(0, len(items), batchSize):
        yield items[i: i + batchSize]