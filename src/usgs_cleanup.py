import os.path
import pandas as pd


def cleanup_usgs_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, "data")
    raw_file_path = os.path.join(data_path, "raw", "JAPAN_USGS.csv")
    file_path = os.path.join(data_path, "clean", "cleaned_usgs.csv")

    if not os.path.exists(raw_file_path):
        return False

    raw_df = pd.read_csv(raw_file_path)
    renamed_df = raw_df.rename(columns={'mag': 'magnitude', 'id': 'e_id'})
    renamed_df['time'] = pd.to_datetime(renamed_df['time']).dt.strftime("%Y-%m-%d %H:%M:%S")
    target_columns = ['time', 'latitude', 'longitude', 'depth', 'magnitude', 'place', 'source']
    for column in target_columns:
        if column not in renamed_df.columns and column == 'source':
            renamed_df[column] = "usgs"
        elif column not in renamed_df.columns:
            renamed_df[column] = None
    final_df = renamed_df[target_columns]
    final_df.to_csv(file_path, index=False)
    return True


if __name__ == "__main__":
    cleanup_usgs_data()
