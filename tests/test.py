import unittest
import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus     #Encode special characters in password
class TestEarthquake(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Read cleaned earthquake dataset
        cls.df = pd.read_csv("")

        # Connect to PostgreSQL database
        password = quote_plus("")
        cls.engine = create_engine(
            f"postgresql+pyscopg2://postgress:{password}@localhost:5432/earthquake_db"
        )

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