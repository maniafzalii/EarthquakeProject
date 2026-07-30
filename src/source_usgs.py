import os
import requests
from datetime import datetime, timedelta

end_date = datetime.today().date()
start_date = end_date - timedelta(days=30)

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

params = {
    "format": "csv",
    "starttime": str(start_date),
    "endtime": str(end_date),
    "minlatitude": 24,
    "maxlatitude": 46,
    "minlongitude": 123,
    "maxlongitude": 146,
    "minmagnitude": 1
}

s = False
for _ in range(3):
    try:
        response = requests.get(url, params=params, timeout=13)
        response.raise_for_status()
        with open("../data/raw/JAPAN_USGS.csv", "w", encoding="utf-8") as f:
            f.write(response.text)
        s = True
        break
    except requests.exceptions.RequestException as e:
        print("Failed to get data from 'usgs.gov', trying again...")
        s = False

if not s:
    if os.path.exists("../data/raw/JAPAN_USGS.csv"):
        os.remove("../data/raw/JAPAN_USGS.csv")
    print("Failed to get data from 'usgs.gov'")
