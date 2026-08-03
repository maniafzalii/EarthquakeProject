from src.source_usgs import get_usgs_data
from src.source_geofon import scrapping_geo
from src.source_emsc import scrape_emsc
from src.usgs_cleanup import cleanup_usgs_data
from src.emsc_cleanup import emsc_cleanup
from src.dataset_cleanup import preprocess_csv
from src.database_setup import database_setup_and_report
from src.database_cleanup import database_cleanup
from src.analyze import task_10_17, GREEN, RED, RESET
from src.final_conclusions import analyze_database
from src.analyze_plot import generate_plots
from src.export_database import export_database

def main():
    print(f"\n{GREEN}----------------------------------------------------------")
    print("----- Welcome to Japan's earthquakes analyze program -----")
    print(f"----------------------------------------------------------{RESET}\n")

    while True:
        user_input_main = input("Enter 1 to start analyzing (0 to exit): ").strip()
        match user_input_main:
            case "1":
                get_usgs_data()
                scrapping_geo()
                scrape_emsc()
                cleanup_usgs_data()
                emsc_cleanup()
                preprocess_csv()
                database_setup_and_report()
                database_cleanup()
                export_database()
                task_10_17()
                analyze_database()
                generate_plots()
                print(f"{GREEN}----- Analyzing finished -----{RESET}")
                print(f"You can see the charts in 'plots' folder.")
                print(f"{GREEN}----- GoodBye -----{RESET}")
                break
            case "0":
                print(f"{GREEN}----- GoodBye -----{RESET}")
                exit()
            case _:
                print(f"{RED}Invalid input.{RESET}")


if __name__ == "__main__":
    main()