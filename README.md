# YouTube Trending Video Analytics

An end-to-end data engineering and analytics pipeline examining video virality, audience engagement dynamics, and release scheduling across **153,616 verified records** from four major international YouTube markets: **Canada (CA)**, **Great Britain (GB)**, **India (IN)**, and the **United States (US)**.

---

## 📌 Project Overview & Objectives

YouTube's Trending Feed showcases content that captures rapid public interest and cultural conversation. This project builds a complete, reproducible data pipeline and business intelligence platform to answer core creator and marketing questions:

1. **Market Longevity vs. Velocity**: How long does a trending video persist on the charts across different global regions?
2. **Category Reach vs. Engagement**: Which genres drive mass viewership versus high-conversion active audience engagement?
3. **Release Scheduling Optimization**: What are the empirical best days and hours (UTC) to publish videos for algorithmic momentum?
4. **Creator & Media Dominance**: Which media entities consistently dominate recurring trending positions?

---

## 🛠️ Technologies Used

| Domain | Technology |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **Data Processing & ETL** | Pandas, NumPy |
| **Database & Indexing** | SQLite3 (with WAL mode & B-Tree performance indexing) |
| **Exploratory Data Analysis** | Matplotlib, Seaborn, Jupyter Notebook |
| **Interactive Dashboard** | Streamlit, Plotly Express & Graph Objects |

---

## 📊 Dataset Description

The analysis uses historical YouTube trending records originally curated on Kaggle:
- **Total Cleaned Records**: **153,616 rows** across **24 standardized attributes**.
- **Geographic Coverage**:
  - **Canada (CA)**: 40,881 records (24,427 unique videos)
  - **United States (US)**: 40,901 records (6,351 unique videos)
  - **Great Britain (GB)**: 38,745 records (3,272 unique videos)
  - **India (IN)**: 33,089 records (16,307 unique videos)
- **Data Standardization**:
  - Exact verbatim duplicate removal (accounting for scraping overlaps while fully preserving multi-day trending progressions).
  - Standardized timestamps (`trending_date` parsed from `YY.DD.MM` and `publish_time` from ISO 8601).
  - Derived features: `publish_hour`, `publish_day_of_week`, `days_to_trend`, `engagement_rate`, and `like_to_view_ratio`.
  - 100% category ID to category title mapping using official YouTube regional JSON metadata.

---

## 🔍 Key Analytical Findings

1. **Market Velocity Dichotomy**:
   - **Great Britain (GB)** exhibits massive algorithmic stickiness: unique videos average **11.84 days on trending** and gather **5.91M average views**.
   - Conversely, **Canada (CA)** and **India (IN)** function as high-velocity, rapid-turnover markets: videos average only **1.67 and 1.99 days** on trending respectively.
2. **Reach vs. Engagement Trade-Off**:
   - While **Entertainment** (30.7% share) and **Music** (17.7% share) capture nearly half of all trending placements and lead in raw views, **Comedy (5.31%)**, **Education (4.93%)**, and **Howto & Style (4.89%)** generate the highest proportional audience interaction (likes + comments per view).
3. **The 'Friday Boost' & Release Scheduling Arbitrage**:
   - Friday releases achieve the highest average viewership across all markets (**3.98M views and 99,828 likes per video**)—an **89.7% increase** over Monday uploads (2.10M views).
   - Videos published between **04:00 UTC and 05:00 UTC** generate peak compounding views (>6.5M average views), catching early Asian/European morning traffic and late-night US audiences.
4. **Regional Divergence (India's News Surge)**:
   - In Western markets, News & Politics represents under 4% of trending videos. In India, **News & Politics ranks #2** with 4,709 trending records (15.9% of India's feed).
5. **Syndicated Broadcast Dominance**:
   - Recurring leaderboard spots are heavily dominated by traditional talk franchises (*The Late Show with Stephen Colbert*, *TheEllenShow*, *The Tonight Show*) and global sports entertainment (*WWE*), leveraging daily multi-clip publishing.

---

## 📁 Project Folder Structure

```
YouTube_Trending_Video_Analytics/
│
├── Dashboard/
│   └── app.py                      # Interactive Streamlit & Plotly dashboard
│
├── Notebook/
│   └── YouTube_Trending_Video_Analytics_EDA.ipynb   # Complete 12-chart EDA notebook
│
├── Sql/
│   ├── schema.sql                  # Database schema & 7 performance indexes
│   ├── queries.sql                 # 10 production analytical SQL queries
│   ├── load_database.py            # SQLite ingestion & validation script
│   └── youtube_trending.db         # SQLite database (153,616 records)
│
├── src/
│   ├── clean_data.py               # Data cleaning & transformation pipeline
│   └── generate_eda_notebook.py    # Automated notebook generator & executor
│
├── analysis.py                     # CLI report & business insights generator
├── requirements.txt                # Minimal Python dependencies
├── .gitignore                      # Git exclusion rules (data, db, cache)
└── README.md                       # Comprehensive project documentation
```

---

## ⚡ Installation & Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/YouTube_Trending_Video_Analytics.git
cd YouTube_Trending_Video_Analytics
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### A. Run Data Cleaning & Ingestion (Optional if DB already present)
```bash
# Clean raw datasets and export to Data/Cleaned/
python src/clean_data.py

# Load cleaned records into SQLite database
python Sql/load_database.py
```

### B. Run SQL Analytics & Terminal Report
```bash
python analysis.py
```

### C. Launch the Interactive Streamlit Dashboard
To launch the interactive dashboard in your web browser:

```bash
python -m streamlit run Dashboard/app.py
```
*(The dashboard opens automatically at `http://localhost:8501`)*

---

## 🖥️ Interactive Dashboard Features

- **Dynamic Filtering**: Real-time cross-filtering by Country (`All`, `CA`, `US`, `GB`, `IN`) and Video Category.
- **Executive Metric Cards**: Dynamic KPIs tracking Total Records, Unique Videos, Total Views, Total Likes, and Average Engagement Rate.
- **8 Interactive Plotly Visualizations**:
  - Trending records by country
  - Average views by country
  - Top 10 popular categories
  - Top 10 trending channels
  - Average engagement rate by category
  - Average views by publishing weekday (Monday–Sunday)
  - Average views by publishing hour (0–23 UTC)
  - Trending duration per unique video by country
- **Leaderboard**: Searchable table displaying peak viral videos by views, likes, and engagement.
- **Empirical Takeaways**: Contextual strategic business insights derived from actual database calculations.

---

## 📄 License
This project is open-source under the MIT License.
