"""Data layer: Scaffolding Rental Jobs (SQLite + Pandas).

Pricing rule (from the business):
  scaffolding charge = area (length x height, sq ft) x rate per sq ft   (default Rs 10)
  transport charge   = one-time, default Rs 1000
  agreed period      = 15 days
  every extra 15-day block (or part of one) charges the scaffolding amount again:
      1-15 days -> 1x,  16-30 days -> 2x,  31-45 days -> 3x,  and so on
  total = scaffolding charge x blocks + transport
"""
import math
import random
import sqlite3
from datetime import date, timedelta

import numpy as np
import pandas as pd

DB_PATH = "scaffold_jobs.db"
RATE = 10
TRANSPORT = 1000
AGREED_DAYS = 15

DISPLAY_COLS = [
    "job_id", "customer_name", "site_location", "length_ft", "height_ft", "area_sqft",
    "rate_per_sqft", "scaffolding_charge", "transport_charge", "deployment_date",
    "agreed_days", "expected_dismantle_date", "actual_dismantle_date", "days_on_site",
    "extended", "extension_charge", "total_amount", "amount_paid", "amount_due", "status",
]


def connect(path=DB_PATH):
    con = sqlite3.connect(path)
    con.execute("""CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        site_location TEXT NOT NULL,
        length_ft REAL NOT NULL,
        height_ft REAL NOT NULL,
        rate_per_sqft REAL NOT NULL,
        transport_charge REAL NOT NULL,
        deployment_date TEXT NOT NULL,
        agreed_days INTEGER NOT NULL,
        actual_dismantle_date TEXT,
        amount_paid REAL NOT NULL DEFAULT 0)""")
    con.commit()
    return con


def bill(length_ft, height_ft, rate, transport, days, agreed_days=AGREED_DAYS):
    """Return (area, scaffolding_charge, blocks, extension_charge, total) for a stay of `days`."""
    area = length_ft * height_ft
    base = area * rate
    blocks = max(1, math.ceil(max(days, 1) / agreed_days))
    return area, base, blocks, base * (blocks - 1), base * blocks + transport


def jobs_df(con, as_of=None):
    """All jobs with derived columns. Active jobs are billed up to `as_of` (default: today)."""
    as_of = as_of or date.today()
    df = pd.read_sql_query("SELECT * FROM jobs ORDER BY job_id", con)
    if df.empty:
        return pd.DataFrame(columns=DISPLAY_COLS)
    dep = pd.to_datetime(df["deployment_date"])
    end = pd.to_datetime(df["actual_dismantle_date"])
    end_eff = end.fillna(pd.Timestamp(as_of))
    df["area_sqft"] = df["length_ft"] * df["height_ft"]
    df["scaffolding_charge"] = df["area_sqft"] * df["rate_per_sqft"]
    df["expected_dismantle_date"] = (dep + pd.to_timedelta(df["agreed_days"], unit="D")).dt.strftime("%Y-%m-%d")
    df["days_on_site"] = (end_eff - dep).dt.days.clip(lower=1)
    blocks = np.ceil(df["days_on_site"] / df["agreed_days"]).clip(lower=1)
    df["extension_charge"] = df["scaffolding_charge"] * (blocks - 1)
    df["total_amount"] = df["scaffolding_charge"] * blocks + df["transport_charge"]
    df["amount_due"] = df["total_amount"] - df["amount_paid"]
    df["extended"] = np.where(blocks > 1, "Yes", "No")
    df["status"] = np.where(end.isna(), "Active", "Completed")
    return df[DISPLAY_COLS]


def add_job(con, customer, location, length_ft, height_ft, deployment_date,
            amount_paid=0, rate=RATE, transport=TRANSPORT, agreed_days=AGREED_DAYS):
    customer, location = customer.strip(), location.strip()
    if not customer or not location:
        return False, "Customer name and site location are required."
    if length_ft <= 0 or height_ft <= 0:
        return False, "Length and height must be more than 0."
    if rate <= 0 or transport < 0 or amount_paid < 0:
        return False, "Rate must be more than 0, and money values cannot be negative."
    con.execute(
        """INSERT INTO jobs (customer_name, site_location, length_ft, height_ft, rate_per_sqft,
           transport_charge, deployment_date, agreed_days, amount_paid) VALUES (?,?,?,?,?,?,?,?,?)""",
        (customer, location, float(length_ft), float(height_ft), float(rate), float(transport),
         str(deployment_date), int(agreed_days), float(amount_paid)))
    con.commit()
    return True, "Job saved."


def complete_job(con, job_id, dismantle_date):
    """Mark a job dismantled. Returns (ok, message) with the final bill."""
    row = con.execute("SELECT deployment_date, actual_dismantle_date FROM jobs WHERE job_id=?",
                      (int(job_id),)).fetchone()
    if row is None:
        return False, "Job not found."
    if row[1] is not None:
        return False, "This job is already dismantled."
    if str(dismantle_date) < row[0]:
        return False, "Dismantle date cannot be before the deployment date."
    con.execute("UPDATE jobs SET actual_dismantle_date=? WHERE job_id=?", (str(dismantle_date), int(job_id)))
    con.commit()
    j = jobs_df(con).set_index("job_id").loc[int(job_id)]
    return True, (f"Dismantled after {int(j['days_on_site'])} days. Total bill Rs {j['total_amount']:,.0f}, "
                  f"paid Rs {j['amount_paid']:,.0f}, due Rs {j['amount_due']:,.0f}.")


def add_payment(con, job_id, amount):
    j = jobs_df(con).set_index("job_id")
    if int(job_id) not in j.index:
        return False, "Job not found."
    if amount <= 0:
        return False, "Payment must be more than 0."
    due = j.loc[int(job_id), "amount_due"]
    if amount > due:
        return False, f"Payment is more than the amount due (Rs {due:,.0f})."
    con.execute("UPDATE jobs SET amount_paid = amount_paid + ? WHERE job_id=?", (float(amount), int(job_id)))
    con.commit()
    return True, f"Payment of Rs {amount:,.0f} recorded."


# ---------- analytics ----------
def kpis(df):
    done = df[df["status"] == "Completed"]
    return {
        "jobs": len(df),
        "active": int((df["status"] == "Active").sum()),
        "billed": float(df["total_amount"].sum()),
        "collected": float(df["amount_paid"].sum()),
        "due": float(df["amount_due"].sum()),
        "avg_days": float(done["days_on_site"].mean()) if len(done) else 0.0,
        "late_pct": float((done["extended"] == "Yes").mean() * 100) if len(done) else 0.0,
        "extension_revenue": float(df["extension_charge"].sum()),
    }


def monthly_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "jobs", "billed"])
    d = df.assign(month=pd.to_datetime(df["deployment_date"]).dt.strftime("%Y-%m"))
    return d.groupby("month").agg(jobs=("job_id", "count"), billed=("total_amount", "sum")).reset_index()


def by_location(df):
    if df.empty:
        return pd.DataFrame(columns=["site_location", "billed"])
    return (df.groupby("site_location")["total_amount"].sum().sort_values(ascending=False)
              .rename("billed").reset_index())


def top_customers(df):
    if df.empty:
        return pd.DataFrame(columns=["customer_name", "billed", "due"])
    g = df.groupby("customer_name").agg(billed=("total_amount", "sum"), due=("amount_due", "sum"))
    return g.sort_values("billed", ascending=False).reset_index()


def unpaid(df):
    return df[df["amount_due"] > 0].sort_values("amount_due", ascending=False)


def overdue_active(df):
    return df[(df["status"] == "Active") & (df["days_on_site"] > df["agreed_days"])]


def duration_buckets(df):
    done = df[df["status"] == "Completed"]
    order = ["1-15 days", "16-30 days", "31-45 days", "46+ days"]
    d = done["days_on_site"]
    counts = [int(((d >= 1) & (d <= 15)).sum()), int(((d >= 16) & (d <= 30)).sum()),
              int(((d >= 31) & (d <= 45)).sum()), int((d >= 46).sum())]
    return pd.DataFrame({"stay": order, "jobs": counts})


# ---------- demo data ----------
CUSTOMERS = ["Sharma Constructions", "Patel Builders", "Gupta Infra", "Verma & Sons", "Jain Developers",
             "Agrawal Realty", "Mehta Painters", "Singh Contractors", "Rathore Builders", "Malviya Interiors",
             "Choudhary Projects", "Tiwari Constructions", "Khan Facade Works", "Bansal Group"]
LOCATIONS = ["Vijay Nagar", "Palasia", "Rau", "Bhawarkuan", "Sudama Nagar", "Scheme 54",
             "AB Road", "Bengali Square", "Rajendra Nagar", "Mhow"]


def generate_sample_jobs(n=150, as_of=None, seed=7):
    """Realistic but FAKE demo jobs, ending near `as_of`."""
    rnd = random.Random(seed)
    as_of = as_of or date.today()
    start = as_of - timedelta(days=330)
    days_offsets = sorted(rnd.randint(0, 327) for _ in range(n))
    cw = [10, 9, 8, 6, 6, 5, 5, 4, 4, 3, 3, 3, 2, 2]
    rows = []
    for off in days_offsets:
        dep = start + timedelta(days=off)
        cust = rnd.choices(CUSTOMERS, weights=cw)[0]
        loc = rnd.choice(LOCATIONS)
        length = rnd.choice([10, 15, 20, 20, 25, 30, 40, 50])
        height = rnd.choice([10, 15, 20, 20, 25, 30])
        r = rnd.random()
        planned = rnd.randint(10, 15) if r < 0.55 else (rnd.randint(16, 30) if r < 0.83 else rnd.randint(31, 45))
        end = dep + timedelta(days=planned)
        completed = end <= as_of
        shown_days = planned if completed else max((as_of - dep).days, 1)
        _, _, _, _, total = bill(length, height, RATE, TRANSPORT, shown_days)
        if completed:
            recent = (as_of - end).days < 30
            p = rnd.random()
            unpaid_chance = 0.2 if recent else 0.04
            if p < unpaid_chance:
                paid = 0
            elif p < unpaid_chance + 0.12:
                paid = round(total * rnd.uniform(0.4, 0.9), -2)
            else:
                paid = total
        else:
            paid = round(total * 0.5, -2) if rnd.random() < 0.5 else 0
        rows.append((cust, loc, length, height, RATE, TRANSPORT, str(dep), AGREED_DAYS,
                     str(end) if completed else None, float(paid)))
    return rows


def load_sample(con, n=150, as_of=None):
    rows = generate_sample_jobs(n, as_of)
    con.executemany(
        """INSERT INTO jobs (customer_name, site_location, length_ft, height_ft, rate_per_sqft,
           transport_charge, deployment_date, agreed_days, actual_dismantle_date, amount_paid)
           VALUES (?,?,?,?,?,?,?,?,?,?)""", rows)
    con.commit()
    return len(rows)
