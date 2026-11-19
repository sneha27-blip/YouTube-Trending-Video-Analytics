"""
YouTube Trending Video Analytics - Database Loader
File: Sql/load_database.py

This script initializes the SQLite database (Sql/youtube_trending.db), executes
the schema definition (Sql/schema.sql), and loads the cleaned data from
Data/Cleaned/all_countries_cleaned.csv into the trending_videos table.

Features:
- Relative path discovery based on project structure.
- Idempotent schema execution (safe re-runs without duplication).
- Clean data type mapping and boolean conversion.
- Automated row count and country representation verification.
"""

import os
import sqlite3
import time
import pandas as pd


def get_project_root() -> str:
    """Return the absolute path to the project root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, ".."))


def load_database():
    start_time = time.time()
    project_root = get_project_root()
    print(f"Project root: {project_root}")

    # Paths
    csv_path = os.path.join(project_root, "Data", "Cleaned", "all_countries_cleaned.csv")
    db_path = os.path.join(project_root, "Sql", "youtube_trending.db")
    schema_path = os.path.join(project_root, "Sql", "schema.sql")

    # 1. Verify CSV exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at: {csv_path}")

    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema SQL not found at: {schema_path}")

    print(f"\n1. Reading cleaned dataset: {os.path.relpath(csv_path, project_root)} ...")
    df = pd.read_csv(csv_path, encoding="utf-8")
    expected_rows = len(df)
    print(f"   Loaded {expected_rows:,} records from CSV.")

    # Convert boolean columns to integers (0/1) for clean SQLite storage
    bool_cols = ["comments_disabled", "ratings_disabled", "video_error_or_removed"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # 2. Establish SQLite connection
    print(f"\n2. Connecting to SQLite database: {os.path.relpath(db_path, project_root)} ...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("   ✓ Database connection established successfully.")

    # 3. Apply Schema
    print(f"\n3. Applying schema from {os.path.relpath(schema_path, project_root)} ...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Enable WAL mode for high concurrency & speed
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.executescript(schema_sql)
    conn.commit()
    print("   ✓ Table 'trending_videos' and analytical indexes created successfully.")

    # 4. Insert Data
    print(f"\n4. Inserting {expected_rows:,} records into 'trending_videos' ...")
    # Insert using pandas to_sql in chunks for high performance
    df.to_sql(
        name="trending_videos",
        con=conn,
        if_exists="append",
        index=False,
        chunksize=10000
    )
    conn.commit()
    print(f"   ✓ Insert complete.")

    # 5. Verification
    print("\n5. Verifying database records...")
    cursor.execute("SELECT COUNT(*) FROM trending_videos;")
    total_db_rows = cursor.fetchone()[0]
    print(f"   • Database total row count: {total_db_rows:,}")

    cursor.execute("SELECT country, COUNT(*) FROM trending_videos GROUP BY country ORDER BY country;")
    country_counts = cursor.fetchall()
    print("   • Country breakdown:")
    for country, count in country_counts:
        print(f"     - {country}: {count:,} records")

    conn.close()

    elapsed = time.time() - start_time
    print(f"\nDatabase setup and loading finished in {elapsed:.2f} seconds!")
    print(f"Verification status: {'SUCCESS' if total_db_rows == expected_rows else 'FAILED'}")


if __name__ == "__main__":
    load_database()
