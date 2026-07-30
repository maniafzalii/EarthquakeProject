import os.path
import pandas as pd


def cleanup_usgs_data():
    if not os.path.exists("../data/raw/JAPAN_USGS.csv"):
        return False

    raw_df = pd.read_csv('../data/raw/JAPAN_USGS.csv')
    renamed_df = raw_df.rename(columns={'mag': 'magnitude', 'id': 'e_id'})
    renamed_df['time'] = pd.to_datetime(renamed_df['time']).dt.strftime("%Y-%m-%d %H:%M:%S")
    target_columns = ['time', 'latitude', 'longitude', 'depth', 'magnitude', 'place', 'source']
    for column in target_columns:
        if column not in renamed_df.columns and column == 'source':
            renamed_df[column] = "usgs"
        elif column not in renamed_df.columns:
            renamed_df[column] = None
    final_df = renamed_df[target_columns]
    final_df.to_csv('../data/clean/cleaned_usgs.csv', index=False)
    return True


if __name__ == "__main__":
    cleanup_usgs_data()
