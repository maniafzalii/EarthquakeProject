import os
import sys

# Add project root directory to Python path
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, BASE_DIR)

import unittest
import pandas as pd
from sqlalchemy import text
from src.database_setup import get_engine

class TestEarthquake(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Read final earthquake dataset
        csv_path = os.path.join(
            BASE_DIR, "data", "final", "database.csv"
        )

        cls.df = pd.read_csv(csv_path, parse_dates=["time"])

        # Connect to PostgreSQL database
        cls.engine, res = get_engine()

        if not res:
            raise Exception("Database connection failed.")

    # Check CSV structure and missing values
    def test_data_correctly(self):

        self.assertGreater(len(self.df), 0, "CSV file is empty!")

        required_columns = [
            "time",
            "latitude",
            "longitude",
            "depth",
            "magnitude",
            "region",
            "source"
        ]

        for column in required_columns:
            self.assertEqual(
                self.df[column].isnull().sum(),
                0,
                f"Missing values found in {column} column."
            )

    # Check data types
    def test_data_type(self):

        numeric_columns = [
            "latitude",
            "longitude",
            "depth",
            "magnitude"]

        for column in numeric_columns:
            self.assertTrue(
                pd.api.types.is_numeric_dtype(self.df[column]),
                f"Column {column} must be numeric."
            )

        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(self.df["time"]),
            f"Column time must be datetime."
        )

    # Validate statistical values
    def test_statistical_validating(self):
        mean_value = self.df["magnitude"].mean()
        std_value = self.df["magnitude"].std()
        self.assertGreaterEqual(
            mean_value,
            3,
            f"Unexpected magnitude mean: {mean_value}"
        )

        self.assertLessEqual(
            mean_value,
            7,
            f"Unexpected magnitude mean: {mean_value}"
        )

        self.assertLess(
            std_value,
            3,
            f"Unexpected magnitude standard devision: {std_value}"
        )

    # Check inserted record in database    
    def test_database_insert(self):
        with self.engine.connect() as conn:
            db_count = conn.execute(
                text("SELECT COUNT(*) FROM earthquakes")
            ).scalar()


        self.assertEqual(
            db_count, 
            len(self.df),
            f"Row count missmatch: CSV has {len(self.df)}, DB has {db_count}"
        )

    # Close the engine
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "engine"):
            cls.engine.dispose()
