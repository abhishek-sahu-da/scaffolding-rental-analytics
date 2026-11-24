"""
Scaffolding Rental & Analytics
Author: Abhishek Sahu (B.Tech CS - Data Science)
Project Guide: Prof. Manish Thakur

Run with:
    python3 -m streamlit run app.py
"""

# =====================================================================
# Block 1: Imports and Page Setup
# =====================================================================
from datetime import date
import pandas as pd
import streamlit as st
import data

# Configure the Streamlit browser tab, favicon, and responsive wide layout
st.set_page_config(
    page_title="Scaffolding Rental & Analytics",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connect to the local SQLite database and load the full jobs dataset
con = data.connect()
df = data.jobs_df(con)


# =====================================================================
# Block 2: Custom Theme & Professional Styling (Warm Orange Accent)
# =====================================================================
# Inject clean CSS styling to establish a professional construction-tech aesthetic:
# warm orange primary accent (#E8590C), subtle off-white backgrounds, and clean card borders.
st.markdown("""
<style>
    /* Global font adjustments and smooth layout spacing */
    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    /* Branded App Header */
    .app-header {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFFFFF 100%);
        border: 1px solid #FED7AA;
        border-left: 5px solid #E8590C;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .app-header h1 {
        color: #9A3412;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        line-height: 1.2;
    }
    .app-header p {
        color: #64748B;
        font-size: 0.92rem;
        margin: 0.35rem 0 0 0;
    }

    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #FDBA74;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }

    /* Form and Box Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
        border-color: #E2E8F0 !important;
        background-color: #FFFFFF !important;
    }

    /* Primary Action Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #E8590C !important;
        border-color: #E8590C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #C2410C !important;
        border-color: #C2410C !important;
    }

    /* Business Insight Captions under Charts */
    .chart-caption {
        background-color: #FFF7ED;
        border-left: 3px solid #E8590C;
        padding: 0.45rem 0.75rem;
        border-radius: 0 6px 6px 0;
        color: #9A3412;
        font-size: 0.82rem;
        margin-top: 0.3rem;
        margin-bottom: 1rem;
    }

    /* Section Subheadings */
    .section-title {
        color: #1E293B;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# Block 3: Display Formatting Helpers
# =====================================================================
# Prepare column configurations for st.dataframe so all money columns display as
# "Rs 12,500" with thousands separators and dates display in clean readable format.
def get_table_column_config():
    """Return reusable column configurations for formatting dataframe tables."""
    return {
        "job_id": st.column_config.NumberColumn("Job #", format="#%d", width="small"),
        "customer_name": st.column_config.TextColumn("Customer Name", width="medium"),
        "site_location": st.column_config.TextColumn("Site Location", width="medium"),
        "length_ft": st.column_config.NumberColumn("Length", format="%.0f ft", width="small"),
        "height_ft": st.column_config.NumberColumn("Height", format="%.0f ft", width="small"),
        "area_sqft": st.column_config.NumberColumn("Area", format="%,.0f sq ft", width="small"),
        "rate_per_sqft": st.column_config.NumberColumn("Rate/sqft", format="Rs %,.0f", width="small"),
        "scaffolding_charge": st.column_config.NumberColumn("Base Rent", format="Rs %,.0f"),
        "transport_charge": st.column_config.NumberColumn("Transport", format="Rs %,.0f"),
        "deployment_date": st.column_config.DateColumn("Deployed Date", format="YYYY-MM-DD"),
        "agreed_days": st.column_config.NumberColumn("Agreed Stay", format="%d days", width="small"),
        "expected_dismantle_date": st.column_config.DateColumn("Agreed End Date", format="YYYY-MM-DD"),
        "actual_dismantle_date": st.column_config.DateColumn("Actual Dismantle", format="YYYY-MM-DD"),
        "days_on_site": st.column_config.NumberColumn("Days on Site", format="%d days", width="small"),
        "extended": st.column_config.TextColumn("Overran 15d?", width="small"),
        "extension_charge": st.column_config.NumberColumn("Extension Fee", format="Rs %,.0f"),
        "total_amount": st.column_config.NumberColumn("Total Billed", format="Rs %,.0f"),
        "amount_paid": st.column_config.NumberColumn("Amount Paid", format="Rs %,.0f"),
        "amount_due": st.column_config.NumberColumn("Balance Due", format="Rs %,.0f"),
        "status": st.column_config.TextColumn("Status", width="small"),
    }

def prepare_dates_for_display(data_frame):
    """Convert string date columns into pandas datetime objects for clean table rendering."""
    if data_frame.empty:
        return data_frame
    formatted = data_frame.copy()
    for col in ["deployment_date", "expected_dismantle_date", "actual_dismantle_date"]:
        if col in formatted.columns:
            formatted[col] = pd.to_datetime(formatted[col])
    return formatted


# =====================================================================
# Block 4: Sidebar Navigation & "About This Project" Academic Overview
# =====================================================================
# Sidebar Branding
st.sidebar.markdown("""
<div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1rem;">
    <h3 style="color: #E8590C; margin: 0; font-size: 1.25rem; font-weight: 700;">🏗️ SCAF-ANALYTICS</h3>
    <p style="color: #64748B; margin: 0.15rem 0 0; font-size: 0.8rem;">Scaffolding Rental & Operations</p>
</div>
""", unsafe_allow_html=True)

# Navigation Menu with Icons
PAGE_OPTIONS = {
    "📊 Dashboard": "Dashboard",
    "➕ New job": "New job",
    "🔄 Dismantle & payments": "Dismantle & payments",
    "📋 All jobs": "All jobs",
}

selected_page_label = st.sidebar.radio(
    "Navigation",
    list(PAGE_OPTIONS.keys()),
    index=0
)
page = PAGE_OPTIONS[selected_page_label]

# Pricing Rules Summary Card on Sidebar
st.sidebar.markdown("""
<div style="background-color: #FFF7ED; border: 1px solid #FED7AA; border-radius: 8px; padding: 0.75rem; margin-top: 0.5rem; font-size: 0.82rem; color: #7C2D12;">
    <strong>📐 Standard Billing Rule:</strong><br>
    • Scaffolding = Area × Rs 10/sq ft (15 days)<br>
    • Transport = Rs 1,000 (one-time)<br>
    • Extra period: each additional 15-day block (or part thereof) charges the scaffolding base again.
</div>
""", unsafe_allow_html=True)

# "About this project" Comprehensive Academic Section
with st.sidebar.expander("ℹ️ About this project", expanded=False):
    st.markdown("""
    **Project Review 1 · Semester 7**  
    **Scaffolding Inventory & Rental Analytics**  
    *Turning daily site deployments and dismantles into data-driven stock decisions.*

    ---
    **Author:** Abhishek Sahu  
    **Degree:** B.Tech CS (Data Science)  
    **Project Guide:** Prof. Manish Thakur  

    ---
    **1. The Problem (No Records = No Answers):**
    - **Stock is a guess:** Daily site deployments (4+ sites/day) and returns (2+ sites/day) without formal logs leave yard inventory unknown.
    - **Losses go unnoticed:** Lost or unreturned pipes and wheels cannot be proven or recovered.
    - **Buying runs on instinct:** High-demand items stock out while others sit idle.
    - **Billing is hard to settle:** On-site duration is not systematically tracked, leading to disputes and unbilled extension revenue.

    ---
    **2. The Four Analytical Questions:**
    1. Which items are rented the most, and which sit idle?
    2. How much stock is in the yard and how much is out on rent right now?
    3. Which customers and sites bring the most business?
    4. When is demand highest so stock is bought or repaired in time?

    ---
    **3. How the Data Flows:**
    1. **Record:** Log every deployment (length, height, customer, location) & dismantle.
    2. **Store:** Persist data in SQLite database (`scaffold_jobs.db`).
    3. **Clean & Compute:** Pandas engine calculates area, stay days, 15-day blocks, extension charges, and dues.
    4. **Show & Act:** Streamlit interactive interface surfaces real-time overdue alerts, cash collections, and monthly trends.
    """)

# Reusable Sample Data Loading Button
def sample_button():
    """Button to populate the database with 150 realistic sample jobs."""
    if st.button("📥 Load SAMPLE demo data (150 jobs)", type="primary"):
        data.load_sample(con)
        st.success("Successfully loaded 150 sample jobs!")
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reload Demo Data (150 Jobs)", use_container_width=True):
    data.load_sample(con)
    st.rerun()


# =====================================================================
# Main Header Banner (Always Visible on All Pages)
# =====================================================================
st.markdown("""
<div class="app-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
        <div>
            <h1>🏗️ Scaffolding Rental & Analytics</h1>
            <p>Turning daily site deployments and dismantles into data-driven stock & billing decisions</p>
        </div>
        <div>
            <span style="background-color: #FFEDD5; color: #9A3412; font-weight: 600; font-size: 0.78rem; padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid #FDBA74;">
                Operations & Billing System
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================================
# Block 5: Page 1 - Dashboard & Business Intelligence Analytics
# =====================================================================
if page == "Dashboard":
    st.markdown('<div class="section-title">📊 Executive Dashboard & Operational KPIs</div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("ℹ️ No jobs recorded in the database yet. Click below to load demo data or add a new job to view the dashboard.")
        sample_button()
    else:
        # Calculate business key performance indicators using data.kpis()
        k = data.kpis(df)

        # Primary Metric Cards Row (Total Billed, Collected, Money Still Due, Active Jobs)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(
                label="💰 Total Invoiced",
                value=f"Rs {k['billed']:,.0f}",
                help="Total cumulative billings including base scaffolding, transport, and extension fees"
            )
        with m2:
            st.metric(
                label="✅ Collected Revenue",
                value=f"Rs {k['collected']:,.0f}",
                help="Total actual payments received from customers"
            )
        with m3:
            st.metric(
                label="⏳ Money Still Due",
                value=f"Rs {k['due']:,.0f}",
                help="Outstanding receivable balances across all active and completed jobs"
            )
        with m4:
            st.metric(
                label="🏗️ Active On-Site Jobs",
                value=f"{k['active']}",
                help="Total scaffolding jobs currently erected at customer sites"
            )

        # Secondary Operational Metrics Row
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric(label="📋 Total Jobs Logged", value=f"{k['jobs']}")
        with s2:
            st.metric(label="⏱️ Avg Site Stay", value=f"{k['avg_days']:.1f} days")
        with s3:
            st.metric(label="⚠️ Overran 15 Days", value=f"{k['late_pct']:.0f}%")
        with s4:
            st.metric(label="📈 Extension Revenue", value=f"Rs {k['extension_revenue']:,.0f}")

        st.markdown("<hr style='margin: 1.5rem 0 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # Row 1 of Charts: Monthly Operational Volume & Monthly Revenue
        # -------------------------------------------------------------
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown('<div class="section-title">📈 Monthly Deployments Volume</div>', unsafe_allow_html=True)
            monthly_jobs_df = data.monthly_summary(df).set_index("month")[["jobs"]]
            st.bar_chart(monthly_jobs_df, color="#E8590C")
            st.markdown(
                '<div class="chart-caption">💡 <strong>Business Insight:</strong> '
                'Identifies seasonal fluctuations in construction activity to help plan yard staffing, pipe repairs, and fleet availability.</div>',
                unsafe_allow_html=True
            )
            
        with c_right:
            st.markdown('<div class="section-title">💵 Revenue Billed per Month (Rs)</div>', unsafe_allow_html=True)
            monthly_rev_df = data.monthly_summary(df).set_index("month")[["billed"]]
            st.bar_chart(monthly_rev_df, color="#E8590C")
            st.markdown(
                '<div class="chart-caption">💡 <strong>Business Insight:</strong> '
                'Tracks top-line monthly invoicing momentum to monitor business expansion and forecast upcoming cash collections.</div>',
                unsafe_allow_html=True
            )

        # -------------------------------------------------------------
        # Row 2 of Charts: Geographic Demand & Duration Distribution
        # -------------------------------------------------------------
        g_left, g_right = st.columns(2)
        with g_left:
            st.markdown('<div class="section-title">📍 Revenue by Site Location (Rs)</div>', unsafe_allow_html=True)
            loc_df = data.by_location(df).set_index("site_location")
            st.bar_chart(loc_df, color="#E8590C")
            st.markdown(
                '<div class="chart-caption">💡 <strong>Business Insight:</strong> '
                'Highlights high-earning construction hubs (e.g. Palasia, Rau) where transport routes and client relationships should be prioritized.</div>',
                unsafe_allow_html=True
            )
            
        with g_right:
            st.markdown('<div class="section-title">⏱️ How Long Jobs Stay on Site</div>', unsafe_allow_html=True)
            dur_df = data.duration_buckets(df).set_index("stay")
            st.bar_chart(dur_df, color="#E8590C")
            st.markdown(
                '<div class="chart-caption">💡 <strong>Business Insight:</strong> '
                'Reveals retention behavior—jobs past 15 days generate profitable extension penalties but tie up pipes and wheels in the field.</div>',
                unsafe_allow_html=True
            )

        st.markdown("<hr style='margin: 1.5rem 0 1rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # Actionable Tables: Top Clients, Overdue Active Sites, Unpaid Bills
        # -------------------------------------------------------------
        st.markdown('<div class="section-title">🏆 Top Customers by Invoiced Volume</div>', unsafe_allow_html=True)
        top_df = data.top_customers(df).head(8)
        st.dataframe(
            top_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "customer_name": st.column_config.TextColumn("Customer Name"),
                "billed": st.column_config.NumberColumn("Total Invoiced", format="Rs %,.0f"),
                "due": st.column_config.NumberColumn("Outstanding Due", format="Rs %,.0f"),
            }
        )

        st.markdown('<div class="section-title">⚠️ Active Jobs Past 15 Days (Extension Charges Running)</div>', unsafe_allow_html=True)
        over = data.overdue_active(df)
        if over.empty:
            st.success("🎉 All active deployments are within their agreed 15-day period.")
        else:
            over_display = prepare_dates_for_display(
                over[["job_id", "customer_name", "site_location", "deployment_date", "days_on_site", "total_amount", "amount_due"]]
            )
            st.dataframe(
                over_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "job_id": st.column_config.NumberColumn("Job #", format="#%d"),
                    "customer_name": st.column_config.TextColumn("Customer Name"),
                    "site_location": st.column_config.TextColumn("Site Location"),
                    "deployment_date": st.column_config.DateColumn("Deployment Date", format="YYYY-MM-DD"),
                    "days_on_site": st.column_config.NumberColumn("Days on Site", format="%d days"),
                    "total_amount": st.column_config.NumberColumn("Total Billed", format="Rs %,.0f"),
                    "amount_due": st.column_config.NumberColumn("Amount Due", format="Rs %,.0f"),
                }
            )

        st.markdown('<div class="section-title">💳 Outstanding Balances Requiring Collection (Largest First)</div>', unsafe_allow_html=True)
        unpaid_df = data.unpaid(df)[["job_id", "customer_name", "site_location", "status", "total_amount", "amount_paid", "amount_due"]].head(10)
        st.dataframe(
            unpaid_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "job_id": st.column_config.NumberColumn("Job #", format="#%d"),
                "customer_name": st.column_config.TextColumn("Customer Name"),
                "site_location": st.column_config.TextColumn("Site Location"),
                "status": st.column_config.TextColumn("Job Status"),
                "total_amount": st.column_config.NumberColumn("Total Billed", format="Rs %,.0f"),
                "amount_paid": st.column_config.NumberColumn("Amount Paid", format="Rs %,.0f"),
                "amount_due": st.column_config.NumberColumn("Balance Due", format="Rs %,.0f"),
            }
        )


# =====================================================================
# Block 6: Page 2 - New Job Deployment Form & Live Price Preview
# =====================================================================
elif page == "New job":
    st.markdown('<div class="section-title">➕ Record a New Site Deployment</div>', unsafe_allow_html=True)
    st.caption("Register client requirements, calculate facade square footage, and preview commercial pricing.")

    # Form grouped in clean columns with helpful placeholders
    with st.container(border=True):
        st.markdown("##### 🏢 Client & Site Information")
        c1, c2 = st.columns(2)
        customer = c1.text_input(
            "Customer Name",
            placeholder="e.g. Sharma Constructions or Patel Builders",
            help="Full business name of the builder or contractor"
        )
        location = c2.text_input(
            "Site Location (Area / Locality)",
            placeholder="e.g. Vijay Nagar, Rau, Scheme 54",
            help="Site destination or locality in Indore"
        )

        st.markdown("##### 📐 Scaffolding Dimensions")
        d1, d2 = st.columns(2)
        length = d1.number_input(
            "Length (ft)",
            min_value=1.0,
            value=20.0,
            step=1.0,
            help="Horizontal span of scaffolding"
        )
        height = d2.number_input(
            "Height (ft)",
            min_value=1.0,
            value=10.0,
            step=1.0,
            help="Vertical height of scaffolding"
        )

        st.markdown("##### 💰 Commercial Terms & Deployment Date")
        t1, t2, t3, t4 = st.columns(4)
        dep_date = t1.date_input("Deployment Date", value=date.today())
        advance = t2.number_input(
            "Advance Paid (Rs)",
            min_value=0.0,
            value=0.0,
            step=100.0,
            help="Initial deposit received upon deployment"
        )
        rate = t3.number_input(
            "Rate per sq ft (Rs)",
            min_value=1.0,
            value=float(data.RATE),
            step=1.0,
            help="Standard billing rate (default Rs 10 / sq ft)"
        )
        transport = t4.number_input(
            "Transport Charge (Rs)",
            min_value=0.0,
            value=float(data.TRANSPORT),
            step=100.0,
            help="One-time flat delivery & pickup fee"
        )

    # Live Commercial Price Preview Card
    area, base, _, _, total = data.bill(length, height, rate, transport, 1)
    total_30 = data.bill(length, height, rate, transport, 20)[4]
    total_45 = data.bill(length, height, rate, transport, 35)[4]
    balance_due = max(0.0, total - advance)

    st.markdown("##### 🧾 Live Commercial Price Preview")
    with st.container(border=True):
        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("📐 Total Area", f"{area:,.0f} sq ft")
        p2.metric("🧱 Base Scaffolding (15d)", f"Rs {base:,.0f}")
        p3.metric("🚚 Transport Fee (1x)", f"Rs {transport:,.0f}")
        p4.metric("🧾 Total (15-Day Base)", f"Rs {total:,.0f}")
        p5.metric("⏳ Balance Due on Delivery", f"Rs {balance_due:,.0f}")

        st.info(
            f"📌 **Pricing Rule:** Scaffolding charge = {length:.0f} ft × {height:.0f} ft × Rs {rate:.0f}/sq ft = "
            f"**Rs {base:,.0f}** (covers initial {data.AGREED_DAYS} days) + Transport **Rs {transport:,.0f}** = "
            f"**Rs {total:,.0f}** total.\n\n"
            f"⏱️ **Extension Fee Projections:** Each additional 15-day block (or fraction) incurs the base charge (**Rs {base:,.0f}**) again:\n"
            f"• Stay 16–30 days: **Rs {total_30:,.0f}** (+1 extension block)\n"
            f"• Stay 31–45 days: **Rs {total_45:,.0f}** (+2 extension blocks)"
        )

    # Form Submission Button
    if st.button("💾 Save Job Deployment", type="primary", use_container_width=True):
        ok, msg = data.add_job(con, customer, location, length, height, dep_date, advance, rate, transport)
        if ok:
            st.success(f"✅ {msg}")
            st.rerun()
        else:
            st.error(f"❌ {msg}")


# =====================================================================
# Block 7: Page 3 - Dismantle Settlement & Payment Processing
# =====================================================================
elif page == "Dismantle & payments":
    st.markdown('<div class="section-title">🔄 Site Dismantles & Payment Collections</div>', unsafe_allow_html=True)
    st.caption("Mark sites as dismantled, calculate final overstay extension charges, and log customer payment receipts.")

    col_dismantle, col_payment = st.columns(2)

    # -----------------------------------------------------------------
    # Left Column: Dismantle a Job
    # -----------------------------------------------------------------
    with col_dismantle:
        with st.container(border=True):
            st.markdown("#### 🏗️ Dismantle a Job (Return Equipment)")
            st.caption("Select an active site deployment to close out and calculate final bill based on duration on site.")
            
            active = df[df["status"] == "Active"]
            if active.empty:
                st.info("ℹ️ No active jobs currently on site.")
            else:
                labels = {
                    int(r.job_id): f"Job #{int(r.job_id)}: {r.customer_name} — {r.site_location} (Deployed {r.deployment_date}, {int(r.days_on_site)}d on site)"
                    for r in active.itertuples()
                }
                job = st.selectbox("Select Active Job to Dismantle", list(labels.keys()), format_func=lambda i: labels[i])
                end_date = st.date_input("Actual Dismantle Date", value=date.today(), key="end_date")

                # Dynamic bill preview for selected active job
                sel_active = active[active["job_id"] == job].iloc[0]
                dep_dt = pd.to_datetime(sel_active["deployment_date"]).date()
                stay_days = max(1, (end_date - dep_dt).days)
                _, p_base, p_blocks, p_ext, p_total = data.bill(
                    sel_active["length_ft"], sel_active["height_ft"], sel_active["rate_per_sqft"], sel_active["transport_charge"], stay_days
                )
                p_due = max(0.0, p_total - sel_active["amount_paid"])

                st.markdown(
                    f"""<div style="background-color: #FFF7ED; border: 1px solid #FED7AA; padding: 0.85rem 1rem; border-radius: 8px; margin: 0.75rem 0; font-size: 0.88rem; color: #1F2933;">
                        <span style="font-size: 0.8rem; color: #9A3412; font-weight: 700; text-transform: uppercase;">Final Settlement Preview</span><br>
                        <strong>Duration on Site:</strong> {stay_days} days ({p_blocks} × 15-day block{'s' if p_blocks > 1 else ''})<br>
                        <strong>Base Scaffolding:</strong> Rs {p_base:,.0f} | <strong>Extension Charges:</strong> Rs {p_ext:,.0f}<br>
                        <strong>Total Final Bill:</strong> Rs {p_total:,.0f} | <strong>Already Paid:</strong> Rs {sel_active['amount_paid']:,.0f}<br>
                        <strong style="color: #C2410C; font-size: 0.95rem;">Net Balance Due: Rs {p_due:,.0f}</strong>
                    </div>""",
                    unsafe_allow_html=True
                )

                if st.button("✅ Confirm Dismantle & Finalize Bill", type="primary", use_container_width=True):
                    ok, msg = data.complete_job(con, job, end_date)
                    if ok:
                        st.success(f"🎉 {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

    # -----------------------------------------------------------------
    # Right Column: Record a Payment
    # -----------------------------------------------------------------
    with col_payment:
        with st.container(border=True):
            st.markdown("#### 💳 Record a Payment Receipt")
            st.caption("Apply incoming payments to settle outstanding accounts receivable.")
            
            owing = df[df["amount_due"] > 0]
            if owing.empty:
                st.success("🎉 All accounts are fully settled! No pending amounts due.")
            else:
                labels2 = {
                    int(r.job_id): f"Job #{int(r.job_id)}: {r.customer_name} ({r.site_location}) — Due: Rs {r.amount_due:,.0f}"
                    for r in owing.itertuples()
                }
                job2 = st.selectbox("Select Job with Balance Due", list(labels2.keys()), format_func=lambda i: labels2[i])

                sel_owing = owing[owing["job_id"] == job2].iloc[0]
                k1, k2, k3 = st.columns(3)
                k1.metric("Total Billed", f"Rs {sel_owing['total_amount']:,.0f}")
                k2.metric("Paid So Far", f"Rs {sel_owing['amount_paid']:,.0f}")
                k3.metric("Balance Due", f"Rs {sel_owing['amount_due']:,.0f}")

                amount = st.number_input(
                    "Amount Received (Rs)",
                    min_value=0.0,
                    max_value=float(sel_owing["amount_due"]),
                    value=float(sel_owing["amount_due"]),
                    step=100.0,
                    help="Enter the received amount (cannot exceed outstanding balance)"
                )

                if st.button("💵 Save Payment Receipt", type="primary", use_container_width=True):
                    ok, msg = data.add_payment(con, job2, amount)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# =====================================================================
# Block 8: Page 4 - All Jobs Master Audit Table & CSV Export
# =====================================================================
else:
    st.markdown('<div class="section-title">📋 Master Job Register & Fleet Audit</div>', unsafe_allow_html=True)
    st.caption("Comprehensive historical log of all equipment dispatches, dimensions, durations, and commercial settlements.")

    if df.empty:
        st.info("ℹ️ No jobs recorded yet in the system.")
        sample_button()
    else:
        # Search & Filter Controls
        f1, f2 = st.columns([1, 2])
        status_filter = f1.selectbox("Filter by Status", ["All", "Active", "Completed"])
        search_query = f2.text_input(
            "🔍 Search Customer Name or Site Location",
            placeholder="Type customer or area (e.g. Patel, Vijay Nagar)..."
        )

        view = df if status_filter == "All" else df[df["status"] == status_filter]
        if search_query.strip():
            q = search_query.strip().lower()
            view = view[
                view["customer_name"].str.lower().str.contains(q) |
                view["site_location"].str.lower().str.contains(q)
            ]

        # Filtered Summary Metrics Row
        with st.container(border=True):
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Matching Jobs", f"{len(view)}")
            r2.metric("Filtered Invoiced", f"Rs {view['total_amount'].sum():,.0f}")
            r3.metric("Filtered Collected", f"Rs {view['amount_paid'].sum():,.0f}")
            r4.metric("Filtered Outstanding", f"Rs {view['amount_due'].sum():,.0f}")

        # Formatted Master Dataframe
        display_view = prepare_dates_for_display(view)
        st.dataframe(
            display_view,
            use_container_width=True,
            hide_index=True,
            column_config=get_table_column_config()
        )

        # CSV Download Button
        down_col1, down_col2 = st.columns([3, 1])
        down_col2.download_button(
            "📥 Download Filtered CSV",
            view.to_csv(index=False),
            "scaffolding_jobs.csv",
            "text/csv",
            use_container_width=True
        )
