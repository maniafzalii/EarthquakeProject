from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import os

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


database_url = "postgresql+psycopg2://postgres:Postgre1234567@localhost:5432/earthquake_db"
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

clean_path = "../data/clean"
csv_files = [f for f in os.listdir(clean_path)]
for file in csv_files:
    file_path = os.path.join(clean_path, file)
    df = pd.read_csv(file_path)
    df.to_sql(name="earthquakes", con=engine, if_exists="append", index=False, chunksize=2000)

with engine.connect() as conn:
    row_count = conn.execute(text("SELECT COUNT(*) FROM earthquakes;")).scalar_one()

with engine.connect() as conn:
    cols = conn.execute(text("""
    SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
    FROM information_schema.columns
    WHERE table_schema='public'
    AND table_name='earthquakes'
    ORDER BY ordinal_position;
    """)).mappings().all()

column_count = len(cols)
print("---- earthquakes table report ----")
print(f"Row count   : {row_count}")
print(f"Column count: {column_count}")
print("Columns:")
for c in cols:
    print(f"- {c['column_name']}: {c['data_type']}")
