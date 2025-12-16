from fastapi import FastAPI
from scraper.scraper import SeleniumScraper

app = FastAPI()

@app.get('/')
async def root():
    a=SeleniumScraper()
    return {"message" : a.getDashboard() }