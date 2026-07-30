import os.path
import pandas as pd

if os.path.exists("../data/raw/JAPAN_USGS.csv"):
    raw_df = pd.read_csv('../data/raw/JAPAN_USGS.csv')
    renamed_df = raw_df.rename(columns={'mag': 'magnitude', 'id': 'e_id'})
    columns = ['time', 'latitude', 'longitude', 'depth', 'magnitude', 'place', 'source']
    for column in columns:
        if column not in renamed_df.columns and column == 'source':
            renamed_df[column] = "usgs"
        elif column not in renamed_df.columns:
            renamed_df[column] = None
    final_df = renamed_df[columns]
    final_df.to_csv('../data/clean/cleaned_usgs.csv', index=False)
