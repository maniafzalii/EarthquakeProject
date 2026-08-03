import pandas as pd
import numpy as np
import re
import os

def preprocess_csv():

    try:

        # Define input and output paths dynamically based on project root
        BASE_DIR = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        input_path = os.path.join(
            BASE_DIR, "data", "raw", "JAPAN_DATASET.csv"
        )

        output_path = os.path.join(
            BASE_DIR,"data", "clean", "cleaned_dataset.csv"

        )

        # load Raw CSV
        df = pd.read_csv(input_path)

        # Basic Cleaning
        df = df.drop(columns=["status", "notes"],errors="ignore")

        df = df.rename(columns={"mag": "magnitude"})

        # Time Cleaning
        df["time"] = (df["time"].astype(str).str.strip().str.replace(".Z", "Z", regex=False))

        def parse_time(x):

            if pd.isna(x):
                return pd.NaT

            x = str(x).strip()

            # Format: 25/07/2025 12:30:00
            try:
                return pd.to_datetime(
                    x,
                    format="%d/%m/%Y %H:%M:%S",
                    utc=True
                )
            except:
                pass

            # Format: ISO format -> 2025-07-25T12:30:00Z
            try:
                return pd.to_datetime(
                    x,
                    format="ISO8601",
                    utc=True
                )
            except:
                pass

            # Format: Jul 25, 2025, 12:30:00
            try:
                return pd.to_datetime(
                    x,
                    format="%b %d, %Y, %H:%M:%S",
                    utc=True
                )
            except:
                pass

            # Format: 2025-07-25 12:30 PM
            try:
                return pd.to_datetime(
                    x,
                    format="%Y-%m-%d %I:%M %p",
                    utc=True
                )
            except:
                pass

            return pd.NaT

        df["time"] = df["time"].apply(parse_time)
        df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

        # Magnitude Cleaning
        df["magnitude"] = (df["magnitude"].astype(str).str.lower()
            .replace({"four" : "4.0","four.nine" : "4.9","five" : "5.0","five point three" : "5.3"})
        )

        # Numeric Cleaning
        def extract_numeric(value, column):

            if pd.isna(value):
                return np.nan

            value = str(value).strip().lower()

            #depth units
            if column == "depth":
                if "meter" in value or "meters" in value:
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", value)
                    if nums:
                        return float(nums[0]) / 1000

                if "mile" in value or "miles" in value:
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", value)
                    if nums:
                        return float(nums[0]) * 1.60934

            nums = re.findall(r"[-+]?\d*\.\d+|\d+",value)

            return float(nums[0]) if nums else np.nan

        numeric_columns = [
            "latitude",
            "longitude",
            "depth",
            "magnitude"
        ]

        for column in numeric_columns:
            if column in df.columns:
                df[column] = df[column].apply(lambda value: extract_numeric(value, column))

        # Prepare Schema
        columns = [
            "time",
            "latitude",
            "longitude",
            "depth",
            "magnitude",
            "place",
            "source"
        ]

        for column in columns:
            if column not in df.columns:
                df[column] = None

        df["source"] = "DATASET"

        final_df = df[columns]

        # Save clean CSV

        final_df.to_csv(output_path,index = False,encoding = "utf-8")

        return True

    except Exception as e:

        print(f"Preprocessing failed: {e}")

        return False