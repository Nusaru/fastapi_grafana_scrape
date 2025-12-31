from typing import final

grafanaHomeTitle: final  = "Home - Dashboards - Grafana"

#api Code
volumeStorageCode: final = "Volume Storage"
activeUserCode: final = "Active User"


class CaptionBuilder:
    def __init__(self):
        pass

    def buildTelegramCaptionByCode(self, datas: list, code: str):
        if code == volumeStorageCode:
            return buildCaptionForServerStorage(datas)
        elif code == activeUserCode:
            return buildCaptionForUserActive(datas)

def buildCaptionForServerStorage(datas: list):
        title="Daftar Server Volume > 80%\n"
        caption=""
        serverCaption=""

        for data in datas:
            serverCaption += f"server: {data["instance"]}\n"
            valueCaption=""
            for value in data["values"]:
                if value["value"] > 80:
                    valueCaption += f"-volume {value["volume"]} = {value["value"]}%\n"
            if valueCaption != "":
                caption += serverCaption + valueCaption
            serverCaption=""
            print(f'caption : {caption}')
        return title + caption

def buildCaptionForUserActive(data:list):
        caption = f"User Care Active = {len(data)}"
        return caption