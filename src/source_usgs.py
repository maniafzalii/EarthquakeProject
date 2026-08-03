import os
import requests
from datetime import datetime, timedelta


def get_usgs_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, "data", "raw")
    file_path = os.path.join(data_path, "JAPAN_USGS.csv")

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
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
                print("Data extracted from USGS.")
            return True

        except requests.exceptions.RequestException:
            print("Failed to get data from 'usgs.gov', trying again...")

    if os.path.exists(file_path):
        os.remove(file_path)

    print("Failed to get data from 'usgs.gov'")
    return False


if __name__ == "__main__":
    get_usgs_data()
