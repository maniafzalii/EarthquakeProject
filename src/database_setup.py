from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import declarative_base
import pandas as pd
import os
from dotenv import load_dotenv

Base = declarative_base()


class Earthquake(Base):
    __tablename__ = "earthquakes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(255))
    latitude = Column(String(255))
    longitude = Column(String(255))
    depth = Column(String(255))
    magnitude = Column(String(255))
    place = Column(String(255))
    source = Column(String(255))


def get_engine():
    try:
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError(".env file not created or link not available.")
        engine = create_engine(database_url)
        return engine, True
    except Exception:
        print("failed to create engine.")
        return None, False


def setup_database(engine):
    try:
        Earthquake.__table__.drop(bind=engine, checkfirst=True)
        Earthquake.__table__.create(bind=engine, checkfirst=True)
        return True
    except Exception:
        print(f"Failed to setup database.")
        return False


def insert_clean_data(engine):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    clean_path = os.path.join(project_root, "data", "clean")
    try:
        csv_files = [f for f in os.listdir(clean_path) if f.endswith(".csv")]
        for file in csv_files:
            file_path = os.path.join(clean_path, file)
            df = pd.read_csv(file_path)
            df.to_sql(name="earthquakes", con=engine, if_exists="append", index=False, chunksize=2000)
        return True
    except Exception:
        print(f"Failed to read csv files.")
        return False


def early_database_report(engine):
    try:
        with engine.connect() as conn:
            row_count = conn.execute(text("SELECT COUNT(*) FROM earthquakes;")).scalar_one()
            cols = conn.execute(text("""
            SELECT
            column_name,
            data_type
            FROM information_schema.columns
            WHERE table_name='earthquakes'
            ORDER BY ordinal_position;
            """)).mappings().all()

        column_count = len(cols)
        print("---- earthquakes table report ----")
        print(f"Row count   : {row_count}")
        print(f"Column count: {column_count}")
        print("Columns:")
        for c in cols:
            print(f"- {c['column_name']}: {c['data_type']}")
        return True

    except Exception:
        print(f"Failed to generate report.")
        return False


def database_setup_and_report():
    engine, res = get_engine()
    if res:
        if setup_database(engine):
            if insert_clean_data(engine):
                if early_database_report(engine):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


if __name__ == "__main__":
    database_setup_and_report()