"""
YouTube Trending Video Analytics - Data Cleaning & Transformation Pipeline
File: src/clean_data.py

This script processes extracted YouTube trending video datasets for four countries:
Canada (CA), Great Britain (GB), India (IN), and the United States (US).

It performs:
1. Loading raw category JSON mappings and extracted CSVs.
2. Mapping category_id to human-readable category_title.
3. Adding a country identifier (CA, GB, IN, US).
4. Type standardization (numeric columns, proper boolean columns).
5. Text cleaning (safely handling missing descriptions).
6. Datetime parsing:
   - trending_date (YY.DD.MM -> YYYY-MM-DD)
   - publish_time (ISO 8601 -> datetime)
   - publish_date (YYYY-MM-DD)
   - publish_hour (0-23)
   - publish_day_of_week (e.g., Monday, Tuesday)
7. Calculated metrics:
   - engagement_rate = (likes + comment_count) / views * 100
   - like_to_view_ratio = likes / views * 100
   - days_to_trend = trending_date - publish_date (in days)
8. Exact duplicate removal (retaining legitimate multi-day trending records).
9. Output generation in Data/Cleaned/ for each country and a consolidated dataset.
10. Automated verification and comprehensive summary reporting.
"""

import os
import json
import numpy as np
import pandas as pd


def get_project_root() -> str:
    """Return the absolute path to the project root directory."""
    # When running as src/clean_data.py, project root is one level up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    return project_root


def load_category_mapping(json_path: str, fallback_mapping: dict = None) -> dict:
    """
    Load category ID to title mapping from a YouTube category JSON file.
    Optionally merges with a fallback dictionary for missing categories (e.g., Category 29).
    """
    category_map = {}
    if fallback_mapping:
        category_map.update(fallback_mapping)

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("items", []):
                cat_id = int(item["id"])
                title = item.get("snippet", {}).get("title", f"Category {cat_id}")
                category_map[cat_id] = title
    else:
        print(f"Warning: Category JSON file not found at {json_path}")

    return category_map


def clean_country_dataset(
    csv_path: str,
    country_code: str,
    category_map: dict
) -> tuple[pd.DataFrame, dict]:
    """
    Clean and transform a single country's YouTube dataset.
    
    Returns:
        tuple: (cleaned DataFrame, report statistics dictionary)
    """
    stats = {
        "country": country_code,
        "original_rows": 0,
        "final_rows": 0,
        "duplicates_removed": 0,
        "missing_descriptions": 0,
        "other_missing_values": {},
        "invalid_trending_dates": 0,
        "invalid_publish_times": 0,
        "categories_mapped": 0,
        "categories_unmapped": 0,
    }

    # 1. Load CSV
    df = pd.read_csv(csv_path, encoding="utf-8")
    stats["original_rows"] = len(df)

    # 2. Check and remove exact full-row duplicate records
    # Repeated video_id records across different trending dates are preserved
    initial_len = len(df)
    df = df.drop_duplicates().copy()
    stats["duplicates_removed"] = initial_len - len(df)

    # 3. Handle missing values
    stats["missing_descriptions"] = int(df["description"].isna().sum())
    df["description"] = df["description"].fillna("")
    
    # Check for any other text/column missing values
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0 and col != "description":
            stats["other_missing_values"][col] = null_count
            df[col] = df[col].fillna("")

    # 4. Standardize numeric columns
    numeric_cols = ["views", "likes", "dislikes", "comment_count", "category_id"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 5. Standardize boolean columns
    bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
    for col in bool_cols:
        df[col] = df[col].astype(bool)

    # 6. Parse dates
    # trending_date has format YY.DD.MM (e.g., 17.14.11 -> 2017-11-14)
    trending_dt = pd.to_datetime(df["trending_date"], format="%y.%d.%m", errors="coerce")
    stats["invalid_trending_dates"] = int(trending_dt.isna().sum())

    # publish_time has ISO 8601 format (e.g., 2017-11-10T17:00:03.000Z)
    publish_dt = pd.to_datetime(df["publish_time"], errors="coerce")
    stats["invalid_publish_times"] = int(publish_dt.isna().sum())

    # Derive date attributes
    df["publish_date"] = publish_dt.dt.strftime("%Y-%m-%d")
    df["publish_hour"] = publish_dt.dt.hour.fillna(0).astype(int)
    df["publish_day_of_week"] = publish_dt.dt.day_name()
    df["trending_date"] = trending_dt.dt.strftime("%Y-%m-%d")

    # Format publish_time to consistent ISO string format
    df["publish_time"] = publish_dt.dt.strftime("%Y-%m-%d %H:%M:%S")

    # 7. Map category_id to category_title
    df["category_title"] = df["category_id"].map(category_map)
    # Check if any categories remain unmapped
    unmapped_mask = df["category_title"].isna()
    stats["categories_unmapped"] = int(unmapped_mask.sum())
    stats["categories_mapped"] = int((~unmapped_mask).sum())
    df["category_title"] = df["category_title"].fillna("Unknown Category")

    # 8. Add country identifier
    df["country"] = country_code

    # 9. Calculate analytical metrics
    views = df["views"].to_numpy(dtype=float)
    likes = df["likes"].to_numpy(dtype=float)
    comments = df["comment_count"].to_numpy(dtype=float)

    # Safe division avoiding division by zero
    safe_views = np.where(views > 0, views, np.nan)
    engagement_rate = np.where(views > 0, ((likes + comments) / safe_views) * 100.0, 0.0)
    like_to_view_ratio = np.where(views > 0, (likes / safe_views) * 100.0, 0.0)

    df["engagement_rate"] = np.round(engagement_rate, 4)
    df["like_to_view_ratio"] = np.round(like_to_view_ratio, 4)

    # Calculate days to trend
    trending_date_obj = trending_dt.dt.normalize()
    # Strip timezone for accurate calendar day subtraction
    publish_date_obj = publish_dt.dt.tz_localize(None).dt.normalize() if publish_dt.dt.tz is not None else publish_dt.dt.normalize()
    days_to_trend = (trending_date_obj - publish_date_obj).dt.days
    # Fill any NaNs with 0 and convert to int
    df["days_to_trend"] = days_to_trend.fillna(0).astype(int)

    # 10. Reorder columns logically
    ordered_cols = [
        "video_id",
        "trending_date",
        "title",
        "channel_title",
        "category_id",
        "category_title",
        "publish_time",
        "publish_date",
        "publish_hour",
        "publish_day_of_week",
        "tags",
        "views",
        "likes",
        "dislikes",
        "comment_count",
        "thumbnail_link",
        "comments_disabled",
        "ratings_disabled",
        "video_error_or_removed",
        "description",
        "country",
        "engagement_rate",
        "like_to_view_ratio",
        "days_to_trend"
    ]
    df = df[ordered_cols].copy()
    stats["final_rows"] = len(df)

    return df, stats


def print_country_report(stats: dict, output_path: str):
    """Print a structured cleaning report for a single country."""
    country_names = {
        "CA": "Canada (CA)",
        "GB": "Great Britain (GB)",
        "IN": "India (IN)",
        "US": "United States (US)",
    }
    name = country_names.get(stats["country"], stats["country"])
    print(f"\n========================================================")
    print(f" CLEANING REPORT: {name}")
    print(f"========================================================")
    print(f"  • Original row count      : {stats['original_rows']:,}")
    print(f"  • Duplicates removed      : {stats['duplicates_removed']:,}")
    print(f"  • Final row count         : {stats['final_rows']:,}")
    print(f"  • Missing descriptions    : {stats['missing_descriptions']:,} (safely filled)")
    if stats["other_missing_values"]:
        print(f"  • Other missing values    : {stats['other_missing_values']}")
    else:
        print(f"  • Other missing values    : None (0)")
    print(f"  • Invalid trending dates  : {stats['invalid_trending_dates']}")
    print(f"  • Invalid publish times   : {stats['invalid_publish_times']}")
    print(f"  • Category mapping mapped : {stats['categories_mapped']:,} / {stats['final_rows']:,} ({(stats['categories_mapped']/stats['final_rows'])*100:.2f}%)")
    if stats["categories_unmapped"] > 0:
        print(f"  • Unmapped categories     : {stats['categories_unmapped']:,}")
    print(f"  • Output file saved       : {output_path}")
    print(f"  • Records saved           : {stats['final_rows']:,}")


def main():
    project_root = get_project_root()
    print(f"Project root directory: {project_root}")

    # Define relative paths based on project root
    raw_dir = os.path.join(project_root, "Data", "Raw")
    extracted_dir = os.path.join(project_root, "Data", "Extracted")
    cleaned_dir = os.path.join(project_root, "Data", "Cleaned")
    os.makedirs(cleaned_dir, exist_ok=True)

    # Master category fallback dictionary (from US JSON which contains all 32 YouTube categories including Category 29)
    us_json_path = os.path.join(raw_dir, "US_category_id.json")
    master_categories = load_category_mapping(us_json_path)

    # Configuration for each country
    countries = [
        {
            "code": "CA",
            "csv": os.path.join(extracted_dir, "CAvideos.csv"),
            "json": os.path.join(raw_dir, "CA_category_id (2).json"),
            "out": os.path.join(cleaned_dir, "CAvideos_cleaned.csv"),
        },
        {
            "code": "GB",
            "csv": os.path.join(extracted_dir, "GBvideos.csv"),
            "json": os.path.join(raw_dir, "GB_category_id.json"),
            "out": os.path.join(cleaned_dir, "GBvideos_cleaned.csv"),
        },
        {
            "code": "IN",
            "csv": os.path.join(extracted_dir, "INvideos.csv"),
            "json": os.path.join(raw_dir, "IN_category_id.json"),
            "out": os.path.join(cleaned_dir, "INvideos_cleaned.csv"),
        },
        {
            "code": "US",
            "csv": os.path.join(extracted_dir, "USvideos.csv"),
            "json": os.path.join(raw_dir, "US_category_id.json"),
            "out": os.path.join(cleaned_dir, "USvideos_cleaned.csv"),
        },
    ]

    cleaned_dataframes = []
    all_stats = []

    for item in countries:
        country_code = item["code"]
        csv_path = item["csv"]
        json_path = item["json"]
        out_path = item["out"]

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Extracted CSV not found: {csv_path}")

        # Load category mapping for this country, supplemented with master fallback
        category_map = load_category_mapping(json_path, fallback_mapping=master_categories)

        # Clean dataset
        df_clean, stats = clean_country_dataset(csv_path, country_code, category_map)

        # Save individual cleaned CSV
        df_clean.to_csv(out_path, index=False, encoding="utf-8")
        stats["out_path"] = out_path

        cleaned_dataframes.append(df_clean)
        all_stats.append(stats)

        print_country_report(stats, out_path)

    # Create combined dataset
    combined_df = pd.concat(cleaned_dataframes, ignore_index=True)
    combined_out_path = os.path.join(cleaned_dir, "all_countries_cleaned.csv")
    combined_df.to_csv(combined_out_path, index=False, encoding="utf-8")

    print(f"\n========================================================")
    print(f" CONSOLIDATED CLEANED DATASET SUMMARY")
    print(f"========================================================")
    print(f"  • Total records across all countries : {len(combined_df):,}")
    print(f"  • Total columns                      : {combined_df.shape[1]}")
    print(f"  • Output file saved                  : {combined_out_path}")

    # Verification step: Load back all 5 cleaned files with Pandas
    print(f"\n========================================================")
    print(f" VERIFYING ALL 5 CLEANED FILES WITH PANDAS")
    print(f"========================================================")
    files_to_verify = [item["out"] for item in countries] + [combined_out_path]
    for file_path in files_to_verify:
        verified_df = pd.read_csv(file_path, encoding="utf-8")
        rel_path = os.path.relpath(file_path, project_root)
        print(f"  ✓ Successfully reloaded: {rel_path} | Rows: {len(verified_df):,} | Cols: {verified_df.shape[1]}")

    print("\nData cleaning and transformation completed successfully!")


if __name__ == "__main__":
    main()
