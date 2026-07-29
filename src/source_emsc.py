import time 
import datetime

def get_current_time():
    date=datetime.datetime.now()
    year=date.strftime("%Y")
    month=date.strftime("%m")
    day=date.strftime("%d")
    print(f"{year}/{month}/{day}")

get_current_time()