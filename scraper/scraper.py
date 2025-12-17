from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class SeleniumScraper:
    def __init__(self):
        option = Options()
        option.add_argument("--headless")
        option.set_preference("app.update.enabled", False)
        option.set_preference("app.update.auto", False)
        option.set_preference("app.update.staging.enabled", False)

        self.driver=webdriver.Firefox(option)

    def getDashboard(self):

        return "This is scraper2"
    
    # def getFromGrafana
