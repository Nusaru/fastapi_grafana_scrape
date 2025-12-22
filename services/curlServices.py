import pycurl
import base64
import time


from io import BytesIO
from collections import defaultdict

from .cryptograph import Crypthograph

class CurlScraping:
    def __init__(self, username: str, password: str):
        self.username = username
        cryptograph = Crypthograph()
        self.password = cryptograph.decrypt(str(password).encode())

    def postPyCurl(self,apiUrl: str, dataPayload, mode: str):
        auth_string = f"{self.username}:{self.password}"

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL,apiUrl)
        curl.setopt(pycurl.POST,1)

        curl.setopt(pycurl.POSTFIELDS, dataPayload)
        encode_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        if mode=="json":
            headers = ["Content-Type: application/json",
                    f"Authorization: Basic {encode_auth}"]
        elif mode=="form":
            headers = ["Content-Type: application/x-www-form-urlencoded",
                    f"Authorization: Basic {encode_auth}"]
        
        curl.setopt(pycurl.HTTPHEADER, headers)
            
        buffer = BytesIO()

        curl.setopt(pycurl.WRITEDATA, buffer)

        try:
            curl.perform()
            response_body = buffer.getvalue().decode('utf-8')
            
        except Exception as e:
            print(e)
        return response_body
    
    def parse(self, rawJson: dict) -> dict:  
        # ========== SQL Data (MySQL/Postgres/MSSQL) ==========
        if "results" in rawJson:
            all_series = []
            listValues=[]
            resultDict={}
            colCount=0

            for key, result in rawJson["results"].items():
                frames = result.get("frames", [])
                for frame in frames:
                    all_series.append({
                        "queryKey": key,
                        "name": frame.get("name", "series"),
                        "columns": frame["schema"]["fields"],
                        "values": frame["data"]["values"]
                    })
            parsed = {"type": "sql", "series": all_series}
            for s in parsed["series"]:
                for column in s["columns"]:
                    for value in s["values"][colCount]:
                        listValues.append(value)

                    resultDict.update({column['name']:listValues})
                    listValues=[]
                    colCount+=1
            resultList = self.columnToRow(resultDict)
            return resultList
        
        # ========== Prometheus/VictoriaMetrics ==========
        if "data" in rawJson and "result" in rawJson["data"]:
            series = []
            for item in rawJson["data"]["result"]:
                # name = json.load(str(item.get("metric")))
                name = item['metric']
                series.append({
                    "instance": name["instance"],
                    "volume": name["volume"],
                    "columns": ["timestamp", "value"],
                    "values": item["values"][-1]
                })
            grouped = self.groupByInstance(series)

            return grouped
        
        # ========== Loki ==========
        if "data" in rawJson and "result" in rawJson["data"] and isinstance(rawJson["data"]["result"], list):
            if "streams" in rawJson["data"]["result"][0]:
                series = []
                for stream in rawJson["data"]["result"]:
                    series.append({
                        "name": stream.get("stream", {}),
                        "columns": ["timestamp", "log"],
                        "values": stream["values"]
                    })
                return {"type": "loki", "series": series}
        
        # ========== InfluxDB / Flux ==========
        if "results" in rawJson and "tables" in rawJson["results"]:
            series = []
            for table in rawJson["results"]["tables"]:
                columns = table["columns"]
                values = table["values"]
                series.append({
                    "name": table.get("name", "series"),
                    "columns": columns,
                    "values": values
                })
            return {"type": "influx", "series": series}
        
        return {"type": "json", "series": [{"name": "data", "columns": [], "values": [rawJson]}]}
    
    def columnToRow(self, data: dict):
        keys = list(data.keys())
        rows = zip(*data.values())

        return [
            {
                k.lower().replace("",""): v
                for k,v in zip(keys,row)
            }
            for row in rows
        ]

    def groupByInstance(self,datas: list):
        grouped = defaultdict(list)

        for data in datas:
            instance = data.get("instance")
            volume = data.get("volume")

            entry = {
                "value": data["values"][-1]
            }

            if volume is not None:
                entry["volume"] = volume
            
            grouped[instance].append(entry)

        return [
            {
                "instance":instances,
                "values": values
            }
            for instances, values in grouped.items()
        ]
            

def getRangeSixHours():
    timeRange={
        "now": str(int(time.time())),
        "pastSixHour": str((int(time.time())-(6*60*60)))
    }
    return timeRange

