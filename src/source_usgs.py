import os
import requests
from datetime import datetime, timedelta


def get_usgs_data():
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

    for _ in range(2):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            with open("../data/raw/JAPAN_USGS.csv", "w", encoding="utf-8") as f:
                f.write(response.text)
            return True

        except requests.exceptions.RequestException as e:
            print("Failed to get data from 'usgs.gov', trying again...")

    if os.path.exists("../data/raw/JAPAN_USGS.csv"):
        os.remove("../data/raw/JAPAN_USGS.csv")

    print("Failed to get data from 'usgs.gov'")
    return False


if __name__ == "__main__":
    get_usgs_data()
