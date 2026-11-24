# 🏗️ Scaffolding Inventory & Rental Analytics

> **Turning daily site deployments and dismantles into data-driven stock & billing decisions.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)

---

## 🎓 Academic Project Overview
- **Author:** Abhishek Sahu
- **Program:** B.Tech Computer Science (Data Science) — Semester 7
- **Project Review:** Review 1
- **Project Guide:** Prof. Manish Thakur

---

## 📌 The Problem: "No Records Means No Answers"
Scaffolding rental yards handle high-turnover daily logistics (4+ site deployments, 2+ dismantles daily) without centralized digital systems:
1. **Stock is a guess:** Nobody knows exactly how many pipes, couplers, and wheels are in the yard versus out on rent.
2. **Losses go unnoticed:** Unreturned or damaged components are difficult to trace, prove, or recover.
3. **Purchasing runs on instinct:** High-demand components stock out during busy construction periods while others sit idle.
4. **Billing is difficult to settle:** Rental duration depends on exact days deployed on site; lack of formal logs leads to disputes and unbilled overruns.

---

## 🎯 Four Key Analytical Objectives
1. **Which items are rented the most, and which sit idle in the yard?**
2. **How much stock is in the yard and how much is out on rent right now?**
3. **Which customers and sites generate the highest revenue?**
4. **When is demand highest, so stock is repaired or purchased ahead of time?**

---

## 📐 Business Logic & Pricing Rules
- **Base Scaffolding Charge:**
  $$\text{Scaffolding Charge} = \text{Length (ft)} \times \text{Height (ft)} \times \text{Rate per sq ft (default Rs 10)}$$
- **Transport Fee:** One-time flat charge of **Rs 1,000** (covers delivery & return haulage).
- **Agreed Base Period:** **15 days**.
- **Overstay Extension Rule:** Every additional 15-day block (or part of one) incurs the full scaffolding charge again:
  - **1–15 days:** $1 \times \text{Base Scaffolding} + \text{Transport}$
  - **16–30 days:** $2 \times \text{Base Scaffolding} + \text{Transport}$
  - **31–45 days:** $3 \times \text{Base Scaffolding} + \text{Transport}$

---

## 🚀 Application Structure (4 Core Pages)

### 1. 📊 Executive Dashboard
- **Top Metric Cards:** Total Invoiced, Collected Revenue, Money Still Due, and Active On-Site Jobs.
- **Secondary KPI Bar:** Total Jobs Logged, Average Site Duration, Extension Overrun Rate (%), and Extension Revenue.
- **Visual Analytics (2 Rows of Charts with Business Insights):**
  - *Monthly Deployments Volume* (seasonality planning).
  - *Monthly Invoiced Revenue* (cash flow monitoring).
  - *Revenue by Site Location* (geographic hotspot identification).
  - *Duration Distribution* (field retention vs. yard turnover).
- **Actionable Financial Tables:** Top 8 clients, active jobs past agreed 15-day period, and outstanding balances requiring collection.

### 2. ➕ New Job Deployment
- Clean multi-column form for registering client details and facade dimensions.
- **Live Commercial Price Preview:** Computes square footage, base 15-day charges, advance deductions, and 30/45-day extension forecasts in real time before saving.

### 3. 🔄 Dismantle & Payments
- **Dismantle Equipment:** Select any active site and calculate the finalized bill with duration on site, extension penalties, and net balance due.
- **Payment Receipt Entry:** Select clients with outstanding balances and apply cash/bank receipts directly against receivables.

### 4. 📋 All Jobs Master Audit Table
- Complete historical ledger of all 150+ equipment deployments.
- Status filters (All / Active / Completed) and instant search across customer names or localities.
- Pre-formatted financial figures (`Rs %,.0f`) and dates (`YYYY-MM-DD`).
- 1-Click CSV export.

---

## 🛠️ Local Installation & Execution

```bash
# 1. Clone the repository
git clone https://github.com/abhishek-sahu-da/scaffolding-rental-analytics.git
cd scaffolding-rental-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit application
python3 -m streamlit run app.py
```

The application will start at `http://localhost:8501`.

---

## 🌐 Free Cloud Deployment (Streamlit Community Cloud)

1. Fork or push this repository to your GitHub account (`https://github.com/abhishek-sahu-da/scaffolding-rental-analytics`).
2. Visit [share.streamlit.io](https://share.streamlit.io/) and sign in with your GitHub account.
3. Click **"New app"**.
4. Select:
   - **Repository:** `abhishek-sahu-da/scaffolding-rental-analytics`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Deploy!"** — Your live app URL will be generated in less than 2 minutes.

---

## 📁 Repository Structure
```
├── app.py                      # Streamlit UI & interactive screens
├── data.py                     # SQLite data layer & billing business logic
├── scaffold_jobs.db            # Pre-populated SQLite database (150 jobs)
├── scaffolding_jobs_sample.csv # Raw sample dataset (150 records)
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml             # Custom theme configuration (warm orange)
└── README.md                   # Project documentation
```
