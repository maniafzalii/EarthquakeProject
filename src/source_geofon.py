import requests, re, pandas
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

url = "https://geofon.gfz.de/eqinfo/list.php"

now = datetime.now()
month_ago = now - timedelta(days=30)
now = now.strftime("%Y-%m-%d")
month_ago = month_ago.strftime("%Y-%m-%d")

params = {
    "datemin": month_ago,
    "datemax": now,
    "latmin": 24,
    "latmax": 46,
    "lonmin": 123,
    "lonmax": 146,
    "magmin": 1,
}

times = []
places = []
depths = []
longitudes = []
latitudes = []
magnitudes = []


def calculate_magnitude(soup):
    magnitudes_1 = soup.find_all('span', class_="magbox")
    for magnitude in magnitudes_1:
        mag = float(magnitude.text.strip())
        magnitudes.append(mag)


def calculate_epicenter(soup):
    epicenters = soup.find_all('div', class_="col-xs-12")
    for epicenter in epicenters:
        if epicenter.get("title") != None:
            data_1 = (epicenter.get('title'))
            longitudes.append(float(data_1.split(', ')[0].replace('°E', '')))
            latitudes.append(float(data_1.split(', ')[1].replace("°N", "")))


def calculate_places(soup):
    places_1 = soup.find_all('strong')
    for place in places_1:
        places.append(place.text)


def calculate_depth(soup):
    depth_1 = soup.find_all('span', class_="pull-right")
    for data_1 in depth_1:
        if re.match(r'^\d', data_1.text.strip()):
            depth = float(data_1.text.strip().replace("*", ""))
            depths.append(depth)


def calculate_time(soup):
    time_1 = soup.find_all('div', class_="col-xs-12")
    for time in time_1:
        if re.match(r"^\d", time.contents[0]):
            time = (time.contents[0].text.replace("\n", ""))
            time = time.split('.')[0]
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            times.append(time)


data = {
    'time': times,
    'latitude': latitudes,
    'longitude': longitudes,
    'depth': depths,
    'magnitude': magnitudes,
    'place': places,
    'source': "GEOFON"

}

page_checking = 40
page = 1
while True:

    params["page"] = page
    response = requests.get(url, params=params)
    soupp = BeautifulSoup(response.content, "html.parser")

    #print(response.status_code)


    def main_geofon():
        calculate_time(soupp)
        calculate_magnitude(soupp)
        calculate_epicenter(soupp)
        calculate_places(soupp)
        calculate_depth(soupp)


    main_geofon()

    if len(magnitudes) < page_checking:
        break
    else:
        params["page"] = page
        page_checking += 40
        page += 1

df = pandas.DataFrame(data)

BASE_DIR = Path(__file__).resolve().parent.parent

output_dir = BASE_DIR / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)
output_clean_dir = BASE_DIR / "data" / "clean"
output_clean_dir.mkdir(parents=True, exist_ok=True)

df.to_csv(output_dir / "JAPAN_GEOFON.csv", index=False)
df.to_csv(output_clean_dir / "cleaned_GEOFON.csv", index=False)