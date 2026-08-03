import os
import unittest

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


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n{GREEN}Press Enter to return to menu...{RESET}")


def run_step(name, func):
    try:
        print(f"\n{GREEN}----- {name} -----{RESET}\n")
        func()
        print(f"\n{GREEN}✔ {name} completed successfully.{RESET}")
    except Exception as e:
        print(f"\n{RED}✘ Error while running {name}:{RESET}")
        print(f"{RED}{e}{RESET}")

    pause()


def collect_and_clean_data():
    get_usgs_data()
    scrapping_geo()
    scrape_emsc()

    cleanup_usgs_data()
    emsc_cleanup()
    preprocess_csv()


def run_tests():
    suite = unittest.defaultTestLoader.discover(
        start_dir="tests",
        pattern="test.py"
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


def run_everything():
    collect_and_clean_data()
    database_setup_and_report()
    database_cleanup()
    export_database()
    run_tests()
    task_10_17()
    analyze_database()
    generate_plots()


def main():

    while True:

        clear_terminal()

        print(f"""{GREEN}
----------------------------------------------------------
----- Welcome to Japan Earthquakes Analyze Program -----
----------------------------------------------------------

====================== MENU ======================

1. Collect and Clean Data
2. Setup Database
3. Clean Database
4. Export Database
5. Run Tests
6. Analyze Data
7. Generate Plots
8. Run Everything

0. Exit

=================================================={RESET}""")
        choice = input("Enter your choice: ").strip()

        match choice:
            case "1":
                run_step("Collect and Clean Data", collect_and_clean_data)
            case "2":
                run_step("Setup Database", database_setup_and_report)
            case "3":
                run_step("Clean Database", database_cleanup)
            case "4":
                run_step("Export Database", export_database)
            case "5":
                run_step("Run Tests", run_tests)
            case "6":
                run_step("Analysis", task_10_17)
                run_step("Final Conclusions", analyze_database)
            case "7":
                run_step("Generate Plots", generate_plots)
            case "8":
                run_step("Run Everything", run_everything)
            case "0":
                print(f"{GREEN}\n----- GoodBye -----{RESET}")
                break
            case _:
                print(f"{RED}\nInvalid input!{RESET}")
                pause()


if __name__ == "__main__":
    main()