from typing import final
import json

grafanaHomeTitle: final  = "Home - Dashboards - Grafana"
grafanaTitle: final  = "Dashboards - Grafana"


#api Code
volumeStorageCode: final = "Volume Storage"
activeUserCode: final = "Active User"
ticketingCountCode: final = "Ticket Count"
serverResponseCode: final = "Server Response"


class CaptionBuilder:
    def __init__(self):
        pass

    def buildTelegramCaptionByCode(self, datas: list, code: str):
        if code == volumeStorageCode:
            return buildCaptionForServerStorage(datas)
        elif code == activeUserCode:
            return buildCaptionForUserActive(datas)
        elif code == ticketingCountCode:
            return buildCaptionForTicketing(datas)
        elif code == serverResponseCode:
            return buildCaptionForServerResponse(datas)
        else: 
            return "No Caption Generated"

def buildCaptionForServerStorage(datas: list):
    title="Daftar Server Volume > 80%\n"
    caption=""
    serverCaption=""

    for data in datas:
        serverCaption += f"server: {data['instance']}\n"
        valueCaption=""
        for value in data["values"]:
            if value["value"] > 80:
                valueCaption += f"-volume {value['volume']} = {value['value']}%\n"
        if valueCaption != "":
            caption += serverCaption + valueCaption
        serverCaption=""
    return title + caption

def buildCaptionForUserActive(datas:list):
    caption = f"User Care Active = {len(datas)}"
    return caption

def buildCaptionForTicketing(datas:list):
    data = datas[0]

    caption = "Ticketing Information\n" \
    f"Total = {data['total']}\n" \
    f"in Progress = {data['in progress']}\n" \
    f"Waiting for Response = {data['waiting for response']}\n" \
    f"Waiting for Assigned = {data['waiting for assigned']}\n" \
    f"Cancelled = {data['cancelled']}\n" \
    f"Closed = {data['closed']}"

    return caption

def buildCaptionForServerResponse(datas:list):
    caption = "server Response Test\n"
    return caption