import os
import pandas as pd
from sqlalchemy import text
from src.database_setup import get_engine

def export_database():

    # Get SQLAlchemy engine and verify database connection
    engine, res = get_engine()

    if not res:
        print("Database connection failed.")
        return

    # Project root directory
    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    # Save exported table into the final data folder
    output_path = os.path.join(
        BASE_DIR, "data", "final", "database.csv"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok = True)

    df = pd.read_sql(text("SELECT * FROM earthquakes"), engine)

    # Export earthquakes table to CSV
    df.to_csv(output_path, index = False)

    engine.dispose()

    print("CSV exported successfully")

if __name__ == "__main__":
    export_database()