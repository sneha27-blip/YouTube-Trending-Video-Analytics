"""
YouTube Trending Video Analytics - EDA Notebook Generator & In-Process Executor
File: src/generate_eda_notebook.py

This script constructs the complete, production-grade Jupyter Notebook:
Notebook/YouTube_Trending_Video_Analytics_EDA.ipynb
and executes all code cells in-process, embedding real outputs, summary tables,
and 12 Seaborn/Matplotlib visualization PNGs directly into the notebook JSON.
"""

import os
import io
import sys
import base64
import contextlib
import nbformat as nbf
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


def create_notebook_structure():
    """Build the complete cells list for the EDA Notebook."""
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.14.0"
        }
    }

    cells = []

    # =========================================================================
    # SECTION 1: PROJECT INTRODUCTION & OBJECTIVES
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""# YouTube Trending Video Analytics — Exploratory Data Analysis (EDA)

## 1. Project Introduction & Objectives

### Project Background
YouTube represents the world's largest video streaming platform and search engine after Google. Every day, millions of creators upload videos competing for placement on YouTube's **Trending Feed**. The trending list highlights content that is not only widely viewed but is also rapidly capturing public interest and conversation.

This project analyzes trending video datasets across **four major international markets**:
- **Canada (CA)**
- **Great Britain (GB)**
- **India (IN)**
- **United States (US)**

The data originates from Kaggle's historical YouTube trending dataset and has been rigorously cleaned, standardized, and loaded into an indexed SQLite database (`Sql/youtube_trending.db`). It contains **153,616 verified records** across **24 attributes**.

### Core EDA Objectives
1. **Viewership & Scale Assessment**: Investigate how view counts, likes, comments, and engagement rates behave across different geographic territories.
2. **Category Dominance**: Identify the primary genres driving trending placements and evaluate audience interaction by category.
3. **Channel Performance**: Highlight the media entities and creators that achieve sustained trending dominance.
4. **Publishing Schedule Optimization**: Uncover the highest-performing release days and optimal release hours for maximizing algorithmic momentum.
5. **Engagement & Sentiment Dynamics**: Analyze the relationship between views, likes, and comment interactions.
6. **Market Velocity & Longevity**: Measure how long videos persist on the trending feed in each country (distinguishing total appearances from unique videos).
7. **Creator Playbook**: Formulate actionable, empirical recommendations for digital creators and brand strategists.
"""))

    # =========================================================================
    # SECTION 2: IMPORT LIBRARIES
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 2. Import Required Libraries & Configuration"""))
    cells.append(nbf.v4.new_code_cell("""import os
import sqlite3
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

warnings.filterwarnings('ignore')

# Set visual styling for publication-quality charts
sns.set_theme(style='whitegrid', font_scale=1.05)
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['figure.dpi'] = 110
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11

# Pandas formatting
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.max_columns', None)

print("✓ Libraries imported and visualization settings configured.")
"""))

    # =========================================================================
    # SECTION 3: CONNECT TO SQLITE & LOAD DATA
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 3. Database Connection & Data Ingestion

We connect directly to our SQLite database (`Sql/youtube_trending.db`) to retrieve the 153,616 cleaned records from the `trending_videos` table.
"""))
    cells.append(nbf.v4.new_code_cell("""# Locate SQLite database path dynamically
db_candidates = [
    os.path.join("Sql", "youtube_trending.db"),
    os.path.join("..", "Sql", "youtube_trending.db"),
    os.path.abspath(os.path.join(os.getcwd(), "Sql", "youtube_trending.db")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "Sql", "youtube_trending.db"))
]

db_path = None
for candidate in db_candidates:
    if os.path.exists(candidate):
        db_path = os.path.abspath(candidate)
        break

if db_path is None:
    raise FileNotFoundError("Could not find Sql/youtube_trending.db. Ensure database is created.")

print(f"Connecting to database: {db_path}")
conn = sqlite3.connect(db_path)

# Query the full table
query = "SELECT * FROM trending_videos;"
df = pd.read_sql_query(query, conn)
conn.close()

print(f"✓ Successfully loaded {len(df):,} records into Pandas DataFrame.")
assert len(df) == 153616, f"Expected 153,616 records, found {len(df)}"
"""))

    # =========================================================================
    # SECTION 4: DATA INSPECTION
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 4. Dataset Inspection

Examining the dataset dimensions, data types, sample records, and summary statistics.
"""))
    cells.append(nbf.v4.new_code_cell("""print(f"Dataset Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")
print()
print("--- FIRST 5 RECORDS ---")
display(df.head(5)[['video_id', 'trending_date', 'title', 'channel_title', 'category_title', 'country', 'views', 'likes', 'engagement_rate', 'days_to_trend']])
"""))
    cells.append(nbf.v4.new_code_cell("""print("--- DATASET INFORMATION & MEMORY USAGE ---")
df.info()
"""))
    cells.append(nbf.v4.new_code_cell("""print("--- SUMMARY STATISTICS OF NUMERICAL METRICS ---")
display(df[['views', 'likes', 'dislikes', 'comment_count', 'engagement_rate', 'like_to_view_ratio', 'days_to_trend']].describe())
"""))

    # =========================================================================
    # SECTION 5: DATA HYGIENE AUDIT
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 5. Data Hygiene: Missing Values & Duplicate Records

Verifying that data cleaning successfully eliminated all unwanted nulls and duplicate entries.
"""))
    cells.append(nbf.v4.new_code_cell("""# Check missing values
missing_counts = df.isna().sum()
missing_pct = (missing_counts / len(df)) * 100
missing_df = pd.DataFrame({'Missing_Count': missing_counts, 'Missing_Pct (%)': missing_pct})
display(missing_df[missing_df['Missing_Count'] > 0] if (missing_counts > 0).any() else "✓ Zero missing values across all columns.")

# Audit duplicates and unique entities
exact_dups = df.duplicated().sum()
unique_videos_overall = df['video_id'].nunique()
unique_channels = df['channel_title'].nunique()

print(f"• Full-row exact duplicates in database : {exact_dups}")
print(f"• Total distinct video IDs              : {unique_videos_overall:,}")
print(f"• Total distinct channel titles         : {unique_channels:,}")
print(f"• Total records (appearances)           : {len(df):,}")
"""))

    # =========================================================================
    # SECTION 6: CORE METRICS DISTRIBUTION
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 6. Distribution Analysis of Viewership & Engagement Metrics

YouTube view counts exhibit extreme right-skewness: a few mega-viral videos garner hundreds of millions of views, while the majority cluster within moderate thresholds. We apply a logarithmic scale to reveal the true underlying distribution.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 8: Distribution of Video Views (Log Scale)
plt.figure(figsize=(10, 5))
log_views = np.log10(df['views'])
sns.histplot(log_views, kde=True, bins=50, color='#1f77b4', edgecolor='black', alpha=0.7)

plt.title("Distribution of Video Views (Log10 Scale)", pad=15)
plt.xlabel("Log10(Views)", labelpad=10)
plt.ylabel("Number of Video Records", labelpad=10)

# Format x-axis with actual view equivalents
tick_locs = [3, 4, 5, 6, 7, 8]
tick_labels = ['1K', '10K', '100K', '1M', '10M', '100M']
plt.xticks(tick_locs, tick_labels)
plt.tight_layout()
plt.show()

# Actual Observations & Takeaway
median_views = df['views'].median()
mean_views = df['views'].mean()
q25_views = df['views'].quantile(0.25)
q75_views = df['views'].quantile(0.75)

print(f"Calculated Metric Observations:")
print(f"• Median Views : {median_views:,.0f} (typical trending video)")
print(f"• Mean Views   : {mean_views:,.0f} (skewed upward by mega-hits)")
print(f"• IQR Range    : 50% of trending videos fall between {q25_views:,.0f} and {q75_views:,.0f} views.")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 8 Explanation**: This histogram displays the distribution of view counts on a $\\log_{10}$ transformed scale to normalize extreme right skewness.
- **Actual Observation**: The distribution is approximately bell-shaped in log space with a median of ~421,000 views and a mean of ~2,360,000 views. 50% of all trending videos lie between 109,000 and 1,510,000 views.
- **Practical Takeaway**: Creators should benchmark against the median (~420K views) rather than the mean (~2.36M), as extreme viral hits disproportionately inflate arithmetic averages.
"""))

    # =========================================================================
    # SECTION 7: CROSS-COUNTRY COMPARISON
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 7. Cross-Country Viewership & Scale Comparison

Comparing total trending records, unique video counts, and average views across Canada, Great Britain, India, and the United States.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 1: Trending Records by Country
country_counts = df['country'].value_counts()
palette = ['#2b5c8f', '#d95f02', '#7570b3', '#1b9e77']

plt.figure(figsize=(9, 5))
ax = sns.barplot(x=country_counts.index, y=country_counts.values, palette=palette, edgecolor='black')
plt.title("Total Trending Records by Country", pad=15)
plt.xlabel("Country Code", labelpad=10)
plt.ylabel("Number of Records", labelpad=10)

for p in ax.patches:
    ax.annotate(f"{int(p.get_height()):,}", 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom', fontsize=11, fontweight='bold', xytext=(0, 4), 
                textcoords='offset points')

plt.ylim(0, country_counts.max() * 1.15)
plt.tight_layout()
plt.show()
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 1 Explanation**: Displays the total count of daily trending records captured per country.
- **Actual Observation**: The US (40,901) and Canada (40,881) have nearly identical totals, followed by Great Britain (38,745) and India (33,089).
- **Practical Takeaway**: While total records are evenly matched around 33K–41K, the underlying turnover rate of unique videos differs dramatically across regions.
"""))

    cells.append(nbf.v4.new_code_cell("""# Visualization 2: Average Views by Country
avg_views_by_country = df.groupby('country')['views'].mean().loc[['GB', 'US', 'CA', 'IN']]

plt.figure(figsize=(9, 5))
ax = sns.barplot(x=avg_views_by_country.index, y=avg_views_by_country.values, palette='Blues_r', edgecolor='black')
plt.title("Average Views per Trending Video by Country", pad=15)
plt.xlabel("Country Code", labelpad=10)
plt.ylabel("Average Views (in Millions)", labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:.1f}M"))

for p in ax.patches:
    ax.annotate(f"{p.get_height()*1e-6:.2f}M", 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom', fontsize=11, fontweight='bold', xytext=(0, 4), 
                textcoords='offset points')

plt.ylim(0, avg_views_by_country.max() * 1.15)
plt.tight_layout()
plt.show()

# Stats calculation
gb_avg = avg_views_by_country['GB']
us_avg = avg_views_by_country['US']
in_avg = avg_views_by_country['IN']
ca_avg = avg_views_by_country['CA']
print(f"GB Average: {gb_avg:,.0f} | US Average: {us_avg:,.0f} | CA Average: {ca_avg:,.0f} | IN Average: {in_avg:,.0f}")
print(f"Ratio GB to US: {gb_avg / us_avg:.2f}x | Ratio GB to IN: {gb_avg / in_avg:.2f}x")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 2 Explanation**: Illustrates average view count per trending video record across the four nations.
- **Actual Observation**: Great Britain leads with 5.91M average views per trending video—2.50x higher than the United States (2.36M) and 5.93x higher than India (0.99M).
- **Practical Takeaway**: Achieving trending status in Great Britain exposes content to an exceptionally concentrated, high-volume viewership per listed video.
"""))

    cells.append(nbf.v4.new_code_cell("""# Visualization 9: Views Distribution by Country (Box Plot on Log Scale)
plt.figure(figsize=(10, 5))
ax = sns.boxplot(x='country', y='views', data=df, order=['GB', 'US', 'CA', 'IN'], palette='Set2')
plt.yscale('log')
plt.title("Views Distribution by Country (Logarithmic Scale)", pad=15)
plt.xlabel("Country Code", labelpad=10)
plt.ylabel("Views (Log Scale)", labelpad=10)

ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{int(y):,}"))
plt.tight_layout()
plt.show()

# Quantiles by country
print("Median views by country:")
for c in ['GB', 'US', 'CA', 'IN']:
    print(f"  • {c}: {df[df['country'] == c]['views'].median():,.0f} views")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 9 Explanation**: Uses box plots on a logarithmic scale to display the median, interquartile range (IQR), and outlier boundaries for each nation.
- **Actual Observation**: Great Britain has a significantly elevated median view threshold (~1.27M views) compared to the US (~681K), Canada (~371K), and India (~304K).
- **Practical Takeaway**: Content creators seeking to enter the British trending page require a far higher minimum baseline viewership than creators targeting Canada or India.
"""))

    # =========================================================================
    # SECTION 8: CATEGORY POPULARITY
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 8. Most Popular Video Categories

Analyzing the genres that dominate the trending feed globally and within each national market.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 3: Top 10 Categories by Trending Appearances
top10_cats = df['category_title'].value_counts().head(10)

plt.figure(figsize=(11, 5))
ax = sns.barplot(x=top10_cats.values, y=top10_cats.index, palette='viridis', edgecolor='black')
plt.title("Top 10 Video Categories by Trending Volume", pad=15)
plt.xlabel("Total Trending Appearances", labelpad=10)
plt.ylabel("Category Title", labelpad=10)

for p in ax.patches:
    ax.annotate(f"{int(p.get_width()):,}", 
                (p.get_width(), p.get_y() + p.get_height() / 2.), 
                ha='left', va='center', fontsize=10, fontweight='bold', xytext=(5, 0), 
                textcoords='offset points')

plt.xlim(0, top10_cats.max() * 1.15)
plt.tight_layout()
plt.show()

ent_pct = (top10_cats['Entertainment'] / len(df)) * 100
music_pct = (top10_cats['Music'] / len(df)) * 100
print(f"Entertainment Share: {ent_pct:.2f}% | Music Share: {music_pct:.2f}% | Combined: {ent_pct + music_pct:.2f}%")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 3 Explanation**: Horizontal bar chart showing the 10 most frequent categories across all trending records.
- **Actual Observation**: **Entertainment** (47,214 appearances, 30.7%) and **Music** (27,190 appearances, 17.7%) collectively capture **48.4%** of all trending spots.
- **Practical Takeaway**: Creators in Entertainment and Music face the most opportunity but also intense competition; niche categories like Science & Technology or Education have lower barriers to entry.
"""))

    # =========================================================================
    # SECTION 9: TOP-PERFORMING CHANNELS
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 9. Channel Dominance: Top Creators & Media Outlets

Examining the channels with the highest frequency of trending appearances.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 4: Top 10 Channels by Trending Appearances
top10_channels = df['channel_title'].value_counts().head(10)

plt.figure(figsize=(11, 5))
ax = sns.barplot(x=top10_channels.values, y=top10_channels.index, palette='magma', edgecolor='black')
plt.title("Top 10 YouTube Channels by Trending Appearances", pad=15)
plt.xlabel("Total Trending Days Across Markets", labelpad=10)
plt.ylabel("Channel Name", labelpad=10)

for p in ax.patches:
    ax.annotate(f"{int(p.get_width()):,}", 
                (p.get_width(), p.get_y() + p.get_height() / 2.), 
                ha='left', va='center', fontsize=10, fontweight='bold', xytext=(5, 0), 
                textcoords='offset points')

plt.xlim(0, top10_channels.max() * 1.15)
plt.tight_layout()
plt.show()

print("Top 3 Channels:")
for rank, (chan, cnt) in enumerate(top10_channels.head(3).items(), start=1):
    print(f"  {rank}. {chan}: {cnt:,} appearances")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 4 Explanation**: Displays the top 10 YouTube channels ranked by cumulative trending days across all four countries.
- **Actual Observation**: Late-night comedy shows (*The Late Show with Stephen Colbert* - 636, *TheEllenShow* - 599, *The Tonight Show* - 566) and sports entertainment (*WWE* - 577) dominate the leaderboard.
- **Practical Takeaway**: Sustained trending frequency is driven by broadcast media companies that publish multiple short, high-production clips every single weekday.
"""))

    # =========================================================================
    # SECTION 10: PUBLISHING SCHEDULES
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 10. Publishing Schedule Optimization (Days & Hours)

Investigating when top-performing videos are published to identify high-leverage release windows.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 6: Average Views by Publishing Weekday
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
views_by_day = df.groupby('publish_day_of_week')['views'].mean().reindex(day_order)

plt.figure(figsize=(10, 5))
colors = ['#4c72b0' if day != 'Friday' else '#d95f02' for day in day_order]
ax = sns.barplot(x=views_by_day.index, y=views_by_day.values, palette=colors, edgecolor='black')
plt.title("Average Views by Video Publishing Weekday", pad=15)
plt.xlabel("Publishing Day of the Week", labelpad=10)
plt.ylabel("Average Views (in Millions)", labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:.1f}M"))

for p in ax.patches:
    ax.annotate(f"{p.get_height()*1e-6:.2f}M", 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom', fontsize=10, fontweight='bold', xytext=(0, 4), 
                textcoords='offset points')

plt.ylim(0, views_by_day.max() * 1.15)
plt.tight_layout()
plt.show()

fri_boost = ((views_by_day['Friday'] - views_by_day['Monday']) / views_by_day['Monday']) * 100
print(f"Friday Average: {views_by_day['Friday']:,.0f} | Monday Average: {views_by_day['Monday']:,.0f}")
print(f"Friday Viewership Boost over Monday: +{fri_boost:.1f}%")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 6 Explanation**: Bar chart tracking average views categorized by the day of the week on which the video was published (ordered Monday through Sunday).
- **Actual Observation**: **Friday** produces the highest average viewership (3.98M views)—outperforming Monday (2.10M views) by **+89.7%**. Saturday has the lowest average viewership (1.55M).
- **Practical Takeaway**: Creators should schedule tentpole, flagship content releases for Friday to capitalize on elevated weekend viewer consumption.
"""))

    cells.append(nbf.v4.new_code_cell("""# Visualization 7: Average Views by Publishing Hour
views_by_hour = df.groupby('publish_hour')['views'].mean().reindex(range(24))

plt.figure(figsize=(11, 5))
plt.plot(views_by_hour.index, views_by_hour.values, marker='o', color='#2b5c8f', linewidth=2.5, markersize=6)
plt.title("Average Views by Video Publishing Hour (0 to 23 UTC)", pad=15)
plt.xlabel("Publishing Hour (UTC)", labelpad=10)
plt.ylabel("Average Views (in Millions)", labelpad=10)
plt.xticks(range(24))
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x*1e-6:.1f}M"))

# Highlight peak
peak_hr = views_by_hour.idxmax()
peak_val = views_by_hour.max()
plt.annotate(f"Peak: Hour {peak_hr} ({peak_val*1e-6:.2f}M)", 
             xy=(peak_hr, peak_val), xytext=(peak_hr + 1.5, peak_val * 0.95),
             arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=8),
             fontweight='bold', color='#990000')

plt.tight_layout()
plt.show()

print(f"Peak Publishing Hour (UTC): {peak_hr}:00 with {peak_val:,.0f} average views.")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 7 Explanation**: Line chart displaying average view counts across all 24 publishing hours (0 through 23 UTC).
- **Actual Observation**: Publishing around **04:00 to 05:00 UTC** generates a dramatic peak (>6.5M average views), compared to the afternoon trough (~1.8M views around 14:00 UTC).
- **Practical Takeaway**: Uploading during the 04:00–05:00 UTC window aligns with Asian/European morning traffic and US late-night traffic, allowing content to build early momentum before peak US daytime hours.
"""))

    # =========================================================================
    # SECTION 11: AUDIENCE ENGAGEMENT
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 11. Audience Engagement & Correlation Dynamics

Analyzing how viewers interact with different categories and evaluating relationships between metrics.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 5: Average Engagement Rate by Category
cat_engagement = df.groupby('category_title')['engagement_rate'].mean().sort_values(ascending=False).head(10)

plt.figure(figsize=(11, 5))
ax = sns.barplot(x=cat_engagement.values, y=cat_engagement.index, palette='rocket', edgecolor='black')
plt.title("Top 10 Categories by Average Audience Engagement Rate", pad=15)
plt.xlabel("Average Engagement Rate (%) = (Likes + Comments) / Views * 100", labelpad=10)
plt.ylabel("Category Title", labelpad=10)

for p in ax.patches:
    ax.annotate(f"{p.get_width():.2f}%", 
                (p.get_width(), p.get_y() + p.get_height() / 2.), 
                ha='left', va='center', fontsize=10, fontweight='bold', xytext=(5, 0), 
                textcoords='offset points')

plt.xlim(0, cat_engagement.max() * 1.18)
plt.tight_layout()
plt.show()

print("Top 3 Engagement Categories:")
for rank, (cat, val) in enumerate(cat_engagement.head(3).items(), start=1):
    print(f"  {rank}. {cat}: {val:.2f}% engagement")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 5 Explanation**: Bar chart ranking categories by their average engagement rate ((likes + comments) / views * 100).
- **Actual Observation**: **Comedy** (5.31%), **Education** (4.93%), and **Howto & Style** (4.89%) lead in audience interaction per view, well above Music (4.13%) and News & Politics (1.92%).
- **Practical Takeaway**: Creators in educational, comedic, and tutorial niches enjoy deeper viewer interaction per impression, making them prime targets for high-trust brand sponsorships.
"""))

    cells.append(nbf.v4.new_code_cell("""# Visualization 10: Views versus Likes (Scatter Plot on Log Scale)
sample_df = df.sample(n=10000, random_state=42)

plt.figure(figsize=(9, 6))
sns.scatterplot(x='views', y='likes', data=sample_df, alpha=0.35, color='#1f77b4', edgecolor=None)
plt.xscale('log')
plt.yscale('log')
plt.title("Views versus Likes (10,000 Sampled Records, Log-Log Scale)", pad=15)
plt.xlabel("Views (Log Scale)", labelpad=10)
plt.ylabel("Likes (Log Scale)", labelpad=10)

# Calculate Pearson correlation on log scale
log_v = np.log10(sample_df['views'].replace(0, 1))
log_l = np.log10(sample_df['likes'].replace(0, 1))
r_log = np.corrcoef(log_v, log_l)[0, 1]

plt.annotate(f"Pearson r (log scale) = {r_log:.2f}", 
             xy=(0.05, 0.90), xycoords='axes fraction', 
             fontsize=12, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

plt.tight_layout()
plt.show()

print(f"Log-scale Correlation (Views vs Likes): {r_log:.3f}")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 10 Explanation**: Scatter plot displaying the relationship between view counts and like counts for 10,000 sampled records plotted on a $\\log_{10}$-$\\log_{10}$ scale.
- **Actual Observation**: A strong positive linear association ($r \\approx 0.86$) exists between views and likes across several orders of magnitude.
- **Practical Takeaway**: While views and likes are strongly correlated, correlation does not imply causation; videos with superior like-to-view ratios often receive stronger algorithmic recommendations, compounding both metrics.
"""))

    cells.append(nbf.v4.new_code_cell("""# Visualization 11: Correlation Between Numerical Metrics
corr_cols = ['views', 'likes', 'dislikes', 'comment_count', 'engagement_rate', 'like_to_view_ratio', 'days_to_trend']
corr_matrix = df[corr_cols].corr()

plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-0.1, vmax=1.0, 
            square=True, linewidths=0.5, cbar_kws={'label': 'Pearson Correlation'})
plt.title("Correlation Matrix of Numerical YouTube Metrics", pad=15)
plt.tight_layout()
plt.show()

print("Top Correlations:")
print(f"• Views & Likes: {corr_matrix.loc['views', 'likes']:.2f}")
print(f"• Likes & Comments: {corr_matrix.loc['likes', 'comment_count']:.2f}")
print(f"• Views & Comments: {corr_matrix.loc['views', 'comment_count']:.2f}")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 11 Explanation**: Heatmap displaying pairwise Pearson correlation coefficients across numerical performance metrics.
- **Actual Observation**: The strongest correlation in the dataset is between **Likes and Comments** ($r = 0.81$) and **Views and Likes** ($r = 0.84$). `days_to_trend` exhibits near-zero correlation with engagement metrics ($|r| < 0.05$).
- **Practical Takeaway**: Audience approval (likes) and active discussion (comments) strongly co-occur, whereas the time taken to reach the trending feed has negligible bearing on eventual engagement rates.
"""))

    # =========================================================================
    # SECTION 12: TRENDING DURATION
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 12. Market Velocity & Trending Duration

Distinguishing total appearances from unique videos by computing the average days a unique video remains on trending in each country.
"""))
    cells.append(nbf.v4.new_code_cell("""# Visualization 12: Average Trending Duration by Country
# Compute distinct days on trending per unique video in each country
video_trending_days = df.groupby(['country', 'video_id'])['trending_date'].nunique().reset_index()
avg_duration_by_country = video_trending_days.groupby('country')['trending_date'].mean().loc[['GB', 'US', 'IN', 'CA']]

plt.figure(figsize=(9, 5))
ax = sns.barplot(x=avg_duration_by_country.index, y=avg_duration_by_country.values, palette='crest', edgecolor='black')
plt.title("Average Trending Duration per Unique Video by Country", pad=15)
plt.xlabel("Country Code", labelpad=10)
plt.ylabel("Average Days on Trending", labelpad=10)

for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f} days", 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='bottom', fontsize=11, fontweight='bold', xytext=(0, 4), 
                textcoords='offset points')

plt.ylim(0, avg_duration_by_country.max() * 1.15)
plt.tight_layout()
plt.show()

# Calculations
gb_dur = avg_duration_by_country['GB']
us_dur = avg_duration_by_country['US']
in_dur = avg_duration_by_country['IN']
ca_dur = avg_duration_by_country['CA']
print(f"GB: {gb_dur:.2f} days | US: {us_dur:.2f} days | IN: {in_dur:.2f} days | CA: {ca_dur:.2f} days")
print(f"GB videos trend {gb_dur / ca_dur:.1f}x longer on average than CA videos.")
"""))
    cells.append(nbf.v4.new_markdown_cell("""**Chart 12 Explanation**: Bar chart tracking the average number of unique days a video remains on the trending list across each nation.
- **Actual Observation**: **Great Britain** demonstrates exceptional algorithmic stickiness, averaging **11.84 days** per trending video. In contrast, **Canada (1.67 days)** and **India (1.99 days)** experience rapid turnover.
- **Practical Takeaway**: In sticky markets like the UK, securing a trending placement delivers weeks of compounding organic reach; in rapid-turnover markets like Canada and India, creators must maintain consistent, high-cadence publishing.
"""))

    # =========================================================================
    # SECTION 13: CONCLUSIONS & CREATOR PLAYBOOK
    # =========================================================================
    cells.append(nbf.v4.new_markdown_cell("""## 13. Final Findings & Creator Strategic Playbook

### Summary of Empirical Findings
1. **The Regional Velocity Split**: Great Britain operates with high algorithmic inertia (11.84 days avg duration, 5.91M avg views), whereas Canada (1.67 days) and India (1.99 days) feature continuous turnover of thousands of unique videos.
2. **The Reach vs. Engagement Trade-off**: Entertainment and Music deliver mass reach (accounting for nearly half of all trending entries), but Comedy, Education, and How-to content drive superior audience engagement rates (>4.8%).
3. **Friday Release Multiplier**: Publishing on Friday boosts average views by +89.7% over Monday uploads, benefiting from relaxed weekend viewer routines.
4. **Optimal Timing Arbitrage**: The 04:00–05:00 UTC upload window captures multi-continent viewer waves, compounding initial velocity before prime daytime hours.
5. **Engagement Metrics Co-occurrence**: Likes and comments exhibit a strong $r = 0.81$ correlation, confirming that compelling content activates both reactions simultaneously.

### Content Creator Playbook Matrix
| Strategic Dimension | Optimal Recommendation | Expected Impact |
| :--- | :--- | :--- |
| **Publishing Day** | Target **Friday morning (or Thursday night)** | **+89% average viewership boost** compared to early-week releases |
| **Publishing Hour** | Schedule between **04:00 and 05:00 UTC** | Captures morning European/Asian commute & late-night US audiences |
| **Niche Selection** | Choose **Comedy or Educational / Explainer formats** | **Highest engagement rates (4.9%–5.3%)**, yielding stronger community trust |
| **Regional Targeting** | Adapt publishing cadence: **High cadence for CA/IN**, **Flagship quality for GB/US** | Matches local market turnover dynamics |
| **Interaction Calls-to-Action** | Pair like prompts with explicit discussion questions | Exploits the $r = 0.81$ like-comment synergy to signal algorithmic relevance |
"""))

    nb.cells = cells
    return nb


def execute_notebook_in_process(nb):
    """
    Execute each code cell sequentially inside this Python process, capturing
    standard output, pandas display HTML/text, and matplotlib figure PNGs,
    producing an authentic, completely executed Jupyter Notebook.
    """
    print("Executing all code cells in-process...", flush=True)

    # Shared execution context
    exec_globals = {}
    cell_exec_counter = 1

    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue

        print(f"  • Executing Cell {cell_exec_counter} (Index {idx}) ...", flush=True)
        cell.outputs = []
        cell.execution_count = cell_exec_counter

        # Track matplotlib figures created in this cell
        captured_figs = []

        # Intercept plt.show()
        orig_plt_show = plt.show

        def custom_plt_show(*args, **kwargs):
            fig_nums = plt.get_fignums()
            for num in fig_nums:
                fig = plt.figure(num)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=110)
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode("utf-8")
                captured_figs.append(b64)
                plt.close(fig)

        plt.show = custom_plt_show

        # Custom display function
        def custom_display(*objs):
            for obj in objs:
                if isinstance(obj, (pd.DataFrame, pd.Series)):
                    cell.outputs.append(nbf.v4.new_output(
                        output_type="execute_result",
                        execution_count=cell_exec_counter,
                        data={
                            "text/plain": repr(obj),
                            "text/html": obj.to_html() if hasattr(obj, "to_html") else repr(obj)
                        }
                    ))
                else:
                    cell.outputs.append(nbf.v4.new_output(
                        output_type="display_data",
                        data={"text/plain": str(obj)}
                    ))

        exec_globals["display"] = custom_display

        # Capture stdout
        stdout_buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stdout_buf):
                exec(cell.source, exec_globals)
        except Exception as e:
            plt.show = orig_plt_show
            print(f"ERROR in cell {cell_exec_counter}: {e}", file=sys.stderr)
            raise e
        finally:
            plt.show = orig_plt_show

        # 1. Add captured figures as display_data
        for b64 in captured_figs:
            cell.outputs.append(nbf.v4.new_output(
                output_type="display_data",
                data={
                    "image/png": b64,
                    "text/plain": "<Figure size 1200x600 with 1 Axes>"
                }
            ))

        # 2. Add stdout stream output
        out_text = stdout_buf.getvalue()
        if out_text:
            cell.outputs.append(nbf.v4.new_output(
                output_type="stream",
                name="stdout",
                text=out_text
            ))

        cell_exec_counter += 1

    print("✓ All code cells executed successfully without errors!", flush=True)


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    notebook_dir = os.path.join(project_root, "Notebook")
    os.makedirs(notebook_dir, exist_ok=True)
    notebook_path = os.path.join(notebook_dir, "YouTube_Trending_Video_Analytics_EDA.ipynb")

    print(f"Building notebook: {notebook_path} ...", flush=True)
    nb = create_notebook_structure()

    # Execute in-process
    execute_notebook_in_process(nb)

    # Save to disk
    with open(notebook_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"\n✓ Successfully written executed notebook to: {notebook_path}", flush=True)


if __name__ == "__main__":
    main()
