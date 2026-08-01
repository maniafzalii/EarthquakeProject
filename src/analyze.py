from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def make_datatype():
    with engine.connect() as conn:
        conn.execute(text("""
        ALTER TABLE earthquakes
        ALTER COLUMN depth TYPE DOUBLE PRECISION
        USING depth::DOUBLE PRECISION;
        """))

        conn.execute(text("""
        ALTER TABLE earthquakes
        ALTER COLUMN magnitude TYPE DOUBLE PRECISION
        USING magnitude::DOUBLE PRECISION;
        """))

        conn.execute(text("""
        ALTER TABLE earthquakes
        ALTER COLUMN time TYPE TIMESTAMP
        USING time::TIMESTAMP;
        """))

        conn.commit()

def earthquake_per_month():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT month,
            COUNT(*) AS earthquake_count
            FROM earthquakes
            GROUP BY month;
        """)).mappings().all()

        for row in result:
            print(f"month: {row['month']}  count: {row['earthquake_count']}")


