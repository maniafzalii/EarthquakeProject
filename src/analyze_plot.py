from src.database_setup import get_engine
import pandas as pd
from sqlalchemy import text
import matplotlib.pyplot as plt
import seaborn as sns
import os


def generate_df(engine):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM earthquakes"))
        df = pd.DataFrame(res.fetchall(), columns=res.keys())
    return df


def histogram_region_magnitude(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "histogram_by_region.png")

    filtered_df = df[["region", "magnitude"]].dropna()
    region_top3 = filtered_df["region"].value_counts().head(3).index
    filtered_df = filtered_df[filtered_df["region"].isin(region_top3)]

    plt.figure(figsize=(10, 6))
    sns.histplot(
        data=filtered_df,
        x="magnitude",
        hue="region",
        bins=20,
        multiple="dodge"
    )

    plt.title("Magnitude distribution for Top 3 regions")
    plt.xlabel("Magnitude")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def linechart_count_time(df):
    pass


def linechart_magnitude_time(df):
    pass


def scatter_magnitude_depth_time(df):
    pass


def boxplot_magnitude_depth(df):
    pass


def heatmap_coordinate_count(df):
    pass


def heatmap_distance_from_tokyo(df):
    pass




def generate_plots():
    engine, res = get_engine()
    if res:
        df = generate_df(engine)
        histogram_region_magnitude(df)


if __name__ == "__main__":
    generate_plots()