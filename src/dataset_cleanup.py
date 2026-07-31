import pandas as pd

raw_df = pd.read_csv("data/raw/JAPAN_DATASET.csv")

cleaned_df = raw_df.drop(columns=["status", "notes"], errors = "ignore")
cleaned_df = cleaned_df.rename(columns={"mag" : "magnitude"})

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
    if column not in cleaned_df.columns:
        cleaned_df[column] = None

cleaned_df["source"] = "DATASET"

final_df = cleaned_df[columns]

final_df.to_csv("data/clean/cleaned_dataset.csv", index = False)