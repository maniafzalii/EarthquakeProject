import numpy as np
from math import radians, sin, cos, sqrt, asin
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

    plt.figure(figsize=(12, 6))
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "linechart_count_time.png")

    date_df = df.copy()
    date_df["date"] = pd.to_datetime(date_df["time"]).dt.date
    count_daily = date_df.groupby("date").size().reset_index(name="count")

    plt.figure(figsize=(12, 6))
    plt.plot(
        count_daily["date"],
        count_daily["count"],
        marker="o",
        linestyle="-"
    )

    plt.title("Earthquakes daily count")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def linechart_avg_magnitude_time(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "linechart_avg_magnitude_time.png")

    date_df = df.copy()
    date_df["date"] = pd.to_datetime(date_df["time"]).dt.date
    avg_daily = date_df.groupby("date")["magnitude"].mean().reser_index(name="average_magnitude")

    plt.figure(figsize=(12, 6))
    plt.plot(
        avg_daily["date"],
        avg_daily["average_magnitude"],
        marker="o",
        linestyle="-"
    )

    plt.title("Earthquakes magnitude daily average")
    plt.xlabel("Date")
    plt.ylabel("Magnitude avg")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def scatter_depth_time(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "scatter_depth_time.png")

    date_df = df.copy()
    date_df["date"] = pd.to_datetime(date_df["time"]).dt.date
    date_df = date_df.dropna(subset=["date", "depth"])

    plt.figure(figsize=(12, 6))
    plt.scatter(
        date_df["date"],
        date_df["depth"],
        alpha=0.5,
        c="orange",
        edgecolors="none"
    )

    plt.title("Earthquakes daily depth")
    plt.xlabel("Date")
    plt.ylabel("Depth (km)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def boxplot_magnitude_depth(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "boxplot_depth_magnitude.png")

    edit_df = df[["depth", "magnitude"]].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    sns.boxplot(
        data=edit_df,
        y="depth",
        ax=axes[0],
        color="blue"
    )
    axes[0].set_title("Earthquake depth distributin")
    axes[0].set_ylabel("Depth (km)")
    axes[0].set_xlabel("Depth")

    sns.boxplot(
        data=edit_df,
        y="magnitude",
        ax=axes[1],
        color="red"
    )
    axes[1].set_title("Earthquake Magnitude Distribution")
    axes[1].set_ylabel("Magnitude")
    axes[1].set_xlabel("Magnitude")

    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def heatmap_locations(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "heatmap_locations.png")

    df_edit = df[["latitude", "longitude"]].dropna()
    heatmap_data, lat, long = np.histogram2d(
        df_edit["latitude"],
        df_edit["longitude"],
        bins=30
    )
    plt.figure(figsize=(12, 6))
    sns.heatmap(
        heatmap_data,
        camp="YlOrRd",
        cbar_kws={"label": "Number of earthquakes"}
    )

    plt.title("Geographical distribution of earthquake")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()


def heatmap_distance_to_tokyo(df):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    plots_path = os.path.join(project_root, "plots")
    file_path = os.path.join(plots_path, "heatmap_distance_from_tokyo.png")

    tokyo_lat = 35.6764
    tokyo_long = 139.65
    df_edit = df[["latitude", "longitude"]].dropna().copy()


    def haversine(la1, lo1, la2, lo2):
        R = 6371
        del_lat = radians(la2 - la1)
        del_lon = radians(lo2 - lo1)
        a = sin(del_lat/2)**2 + cos(radians(la1)) * cos(radians(la2)) * sin(del_lon/2)**2
        c = 2*asin(sqrt(a))
        return R * c


    df_edit["distance_to_tokyo"] = df_edit.apply(lambda row: haversine(row["latitude"], row["longitude"], tokyo_lat, tokyo_long), axis=1)
    df_edit["distance_bin"] = pd.cut(df_edit["distance_to_tokyo"], bins=20)

    heat_data = df_edit["distance_bin"].value_counts().sort_index().values.reshape(-1, 1)
    plt.figure(figsize=(12, 6))
    sns.heatmap(
        heat_data,
        cmap="YlOrRd",
        cbar_kws={"label": "Number of earthquakes"}
    )
    plt.title("Earthquake frequency by distance to tokyo")
    plt.xlabel("Distance bins")
    plt.ylabel("Distance range")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    plt.close()


def generate_plots():
    engine, res = get_engine()
    if res:
        df = generate_df(engine)
        histogram_region_magnitude(df)
        linechart_count_time(df)
        linechart_avg_magnitude_time(df)
        scatter_depth_time(df)
        boxplot_magnitude_depth(df)
        heatmap_locations(df)
        heatmap_distance_to_tokyo(df)


# if __name__ == "__main__":
#     generate_plots()