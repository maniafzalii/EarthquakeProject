from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import time

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
BOLD = '\033[1m'
RESET = '\033[0m'

def connection():
    global engine
    try:
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        print("Connect Successfully\n")
        time.sleep(3)
        if not database_url:
            raise ValueError(".env file not created or link not available.")
        engine = create_engine(database_url)
    except Exception as e:
        print(e)

def earthquake_per_month():
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    with engine.connect() as conn:
        print(f"{YELLOW}{BOLD}Earthquakes per Month\n{RESET}")
        result = conn.execute(text("""
            SELECT month,
            COUNT(*) AS earthquake_count
            FROM earthquakes
            GROUP BY month;
        """)).mappings().all()

        for row in result:
            print(f"Month:{BLUE} {row['month']} {GREEN}|{BLUE} {months[row['month']]} {RESET} Count:{BLUE} {row['earthquake_count']}{RESET}")
        print("\n" * 2)

def group_by_region():
    with engine.connect() as conn:
        task_1 = conn.execute(text("""
            SELECT region,
            COUNT(*) AS earthquake_count
            FROM earthquakes
            GROUP BY region;
        """)).mappings().all()
        print(f"{YELLOW}{BOLD}Earthquakes per Region\n{RESET}")
        for row in task_1:
            print(f"Total Earthquake Happened in {row['region']} is:{BLUE} {row['earthquake_count']} {RESET}\n")
        print("\n")
        time.sleep(1.5)

        task_2 = conn.execute(text("""
        SELECT region,
        ROUND(AVG(magnitude)::numeric, 2) AS avg_magnitude
        FROM earthquakes
        GROUP BY region
        ORDER BY avg_magnitude DESC;
        """)).mappings().all()
        print(f"{YELLOW}{BOLD}AVG Magnitude per Region\n{RESET}")
        for row in task_2:
            print(f"Region:{BLUE} {row['region'].strip()} {RESET}\tAvg_Magnitude:{BLUE} {row['avg_magnitude']}{RESET}\n")
        print("\n")
        time.sleep(1.5)
        task_3 = conn.execute(text("""
        SELECT region,
        ROUND(AVG(depth)::numeric, 2) AS avg_depth
        FROM earthquakes
        GROUP BY region
        ORDER BY avg_depth DESC;
        """)).mappings().all()
        print(f"{YELLOW}{BOLD}AVG Depth per Region\n{RESET}")
        for row in task_3:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}",end="\t")
            print("\n")

        print("\n")
        time.sleep(1.5)
        task_4 = conn.execute(text("""
        SELECT region,
        MAX(magnitude) AS max_magnitude
        FROM earthquakes
        GROUP BY region
        ORDER BY max_magnitude DESC;
        """)).mappings().all()
        print(f"{YELLOW}{BOLD}Max Magnitude per Region\n{RESET}")
        for row in task_4:
            print(f"Region:{BLUE} {row['region'].strip()} {RESET}\tMax_Magnitude:{BLUE} {row['max_magnitude']}{RESET}\n")
        print("\n")
        time.sleep(1.5)
        task_5 = conn.execute(text("""
        SELECT region,
        MAX(depth) AS max_depth,
        MIN(depth) AS min_depth
        FROM earthquakes
        GROUP BY region
        ORDER BY max_depth DESC;
        """)).mappings().all()
        print(f"{YELLOW}{BOLD}Max & Min Depth per Region\n{RESET}")
        for row in task_5:
            print(f"Region:{BLUE} {row['region'].strip()} {RESET}\tMax_Depth:{RED} {row['max_depth']} \t{RESET}Min_Depth:{BLUE} {row['min_depth']}\n{RESET}")

def group_by_region_month_category():
    with engine.connect() as conn:
        print(f"{YELLOW}{BOLD}Grouping By Region-Month-Category\n{RESET}")

        result = conn.execute(text("""
        select region,
        category,
        month,
        count(*) as earthquake_count,
        ROUND(AVG(magnitude)::numeric, 2) AS avg_magnitude,
        ROUND(AVG(depth)::numeric, 2) AS avg_depth
        FROM earthquakes
        GROUP BY region,month,category;
        """)).mappings().all()

        for row in result:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}",end="\t")
            print("\n")

def order_by_time_magnitude():
    print(f"{RED}{BOLD}Most Dangerous Recent Earthquakes\tTOP 10{RESET}\n")
    with engine.connect() as conn:
        result = conn.execute(text("""
        select id,magnitude,time,place,depth,latitude,longitude,source
        FROM earthquakes
        ORDER BY magnitude DESC,time DESC
        LIMIT 10;
        """)).mappings().all()

        for row in result:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}", end="  ")
            print("\n")

def select_magnitude_6_depth_50():
    print(f"{YELLOW}{BOLD}List Of Earthquakes with Magnitude > 6\t Depth < 50\n{RESET}")
    with engine.connect() as conn:
        result = conn.execute(text("""
        select id,magnitude,depth,time,place,latitude,longitude,source
        FROM earthquakes
        WHERE magnitude > 6 And depth < 50
        ORDER BY magnitude DESC;
        """)).mappings().all()
        for row in result:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}", end="  ")
            print("\n")

def count_per_source():
    print(f"{YELLOW}{BOLD}Number of Earthquake per Source\n{RESET}")
    with engine.connect() as conn:
        result = conn.execute(text("""
        select count(*) as Number_of_Earthquakes,source as Source
        FROM earthquakes
        GROUP BY Source
        ORDER BY Number_of_Earthquakes DESC;
        """)).mappings().all()

        for row in result:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}", end="  ")
            print("\n")

def group_by_region_source():
    print(f"{YELLOW}{BOLD}Grouping By Region-Source And You Will See Average Magnitude Per Groups\n{RESET}")
    with engine.connect() as conn:
        result = conn.execute(text("""
        select
        ROUND(AVG(magnitude)::numeric, 2) AS avg_magnitude,
        region,
        source,
        count(*) as earthquake_count
        FROM earthquakes
        group by region,source
        ORDER BY avg_magnitude DESC;
        """)).mappings().all()

        for row in result:
            for key, value in row.items():
                print(f"{key.title()}:{BLUE} {value}{RESET}", end="  ")
            print("\n")

def create_indexes():
    print(f"{YELLOW}{BOLD}Indexing Earthquakes\n{RESET}")
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_earthquakes_region ON earthquakes (region);",
        "CREATE INDEX IF NOT EXISTS idx_earthquakes_time ON earthquakes (time);",
        "CREATE INDEX IF NOT EXISTS idx_earthquakes_magnitude ON earthquakes (magnitude);"
    ]

    with engine.begin() as conn:
        for query in index_queries:
            conn.execute(text(query))
            print(f"{GREEN}{BOLD}Index created successfully for: {query.split('ON')[1]}\n{RESET}")

def task_10_17():
    connection()
    earthquake_per_month()
    time.sleep(1.5)
    group_by_region()
    time.sleep(1.5)
    group_by_region_month_category()
    time.sleep(1.5)
    order_by_time_magnitude()
    time.sleep(1.5)
    select_magnitude_6_depth_50()
    time.sleep(1.5)
    count_per_source()
    time.sleep(1.5)
    group_by_region_source()
    time.sleep(1.5)
    create_indexes()

#task_10_17()


