import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


st.set_page_config(
    page_title="Telecom Warehouse Dashboard", page_icon="📊", layout="wide"
)


def load_local_data():
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    usage = pd.read_csv(DATA_DIR / "usage_records.csv")
    billing = pd.read_csv(DATA_DIR / "billing.csv")
    tickets = pd.read_csv(DATA_DIR / "support_tickets.csv")

    customer_revenue = (
        billing.merge(customers, on="customer_id", how="left")
        .groupby(
            [
                "customer_id",
                "customer_name",
                "country",
                "segment",
                "plan_type",
                "status",
            ],
            as_index=False,
        )
        .agg(total_revenue=("total_amount", "sum"))
    )

    monthly_revenue = billing.groupby("billing_month", as_index=False).agg(
        total_revenue=("total_amount", "sum"),
        collected_revenue=(
            "total_amount",
            lambda values: values[
                billing.loc[values.index, "payment_status"] == "Paid"
            ].sum(),
        ),
        outstanding_revenue=(
            "total_amount",
            lambda values: values[
                billing.loc[values.index, "payment_status"].isin(
                    ["Pending", "Overdue"]
                )
            ].sum(),
        ),
    )

    monthly_revenue["collection_rate_percent"] = (
        monthly_revenue["collected_revenue"]
        / monthly_revenue["total_revenue"]
        * 100
    ).round(2)

    usage_summary = (
        usage.merge(customers, on="customer_id", how="left")
        .groupby(["billing_month", "segment"], as_index=False)
        .agg(
            total_data_gb=("data_gb", "sum"),
            total_voice_minutes=("voice_minutes", "sum"),
            total_sms_count=("sms_count", "sum"),
        )
    )

    support_metrics = tickets.groupby(
        ["severity", "status"], as_index=False
    ).agg(
        ticket_count=("ticket_id", "count"),
        avg_resolution_hours=("resolution_hours", "mean"),
    )

    executive_kpis = pd.DataFrame(
        [
            {
                "total_customers": customers["customer_id"].nunique(),
                "active_customers": customers[customers["status"] == "Active"][
                    "customer_id"
                ].nunique(),
                "total_billed_amount": billing["total_amount"].sum(),
                "total_collected_amount": billing[
                    billing["payment_status"] == "Paid"
                ]["total_amount"].sum(),
                "total_data_gb": usage["data_gb"].sum(),
                "total_support_tickets": tickets["ticket_id"].nunique(),
            }
        ]
    )

    return {
        "executive_kpis": executive_kpis,
        "monthly_revenue": monthly_revenue,
        "customer_revenue": customer_revenue,
        "usage_summary": usage_summary,
        "support_metrics": support_metrics,
    }


def load_snowflake_data():
    conn = st.connection("snowflake")

    return {
        "executive_kpis": conn.query("SELECT * FROM VW_EXECUTIVE_KPIS"),
        "monthly_revenue": conn.query(
            "SELECT * FROM VW_MONTHLY_REVENUE ORDER BY BILLING_MONTH"
        ),
        "customer_revenue": conn.query(
            "SELECT * FROM VW_CUSTOMER_REVENUE ORDER BY TOTAL_REVENUE DESC"
        ),
        "usage_summary": conn.query(
            "SELECT * FROM VW_USAGE_SUMMARY ORDER BY BILLING_MONTH, SEGMENT"
        ),
        "support_metrics": conn.query(
            "SELECT * FROM VW_SUPPORT_METRICS ORDER BY SEVERITY, STATUS"
        ),
    }


def normalize_columns(dataframes):
    normalized = {}

    for name, frame in dataframes.items():
        frame_copy = frame.copy()
        frame_copy.columns = [column.lower() for column in frame_copy.columns]
        normalized[name] = frame_copy

    return normalized


def render_dashboard(data):
    kpis = data["executive_kpis"].iloc[0]

    st.title("Telecom Data Warehouse Dashboard")
    st.caption(
        "Customer, usage, billing, and support analytics using AWS S3, Snowflake, Terraform, and Streamlit."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", int(kpis["total_customers"]))
    col2.metric("Active Customers", int(kpis["active_customers"]))
    col3.metric("Support Tickets", int(kpis["total_support_tickets"]))

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Billed", f"${kpis['total_billed_amount']:,.0f}")
    col5.metric("Total Collected", f"${kpis['total_collected_amount']:,.0f}")
    col6.metric("Total Data Usage", f"{kpis['total_data_gb']:,.0f} GB")

    st.divider()

    monthly_revenue = data["monthly_revenue"]
    customer_revenue = data["customer_revenue"]
    usage_summary = data["usage_summary"]
    support_metrics = data["support_metrics"]

    st.subheader("Monthly Revenue")
    revenue_chart = px.bar(
        monthly_revenue,
        x="billing_month",
        y=["collected_revenue", "outstanding_revenue"],
        barmode="group",
        title="Collected vs Outstanding Revenue",
    )
    st.plotly_chart(revenue_chart, use_container_width=True)

    st.subheader("Top Customers by Revenue")
    top_customers = customer_revenue.sort_values(
        "total_revenue", ascending=False
    ).head(10)
    top_customer_chart = px.bar(
        top_customers,
        x="customer_name",
        y="total_revenue",
        color="segment",
        title="Top Revenue Generating Customers",
    )
    st.plotly_chart(top_customer_chart, use_container_width=True)

    st.subheader("Usage by Customer Segment")
    usage_chart = px.line(
        usage_summary,
        x="billing_month",
        y="total_data_gb",
        color="segment",
        markers=True,
        title="Monthly Data Usage by Segment",
    )
    st.plotly_chart(usage_chart, use_container_width=True)

    st.subheader("Support Ticket Metrics")
    support_chart = px.bar(
        support_metrics,
        x="severity",
        y="ticket_count",
        color="status",
        barmode="group",
        title="Ticket Count by Severity and Status",
    )
    st.plotly_chart(support_chart, use_container_width=True)

    with st.expander("View customer revenue data"):
        st.dataframe(customer_revenue, use_container_width=True)

    with st.expander("View usage summary data"):
        st.dataframe(usage_summary, use_container_width=True)

    with st.expander("View support metrics data"):
        st.dataframe(support_metrics, use_container_width=True)


def main():
    app_mode = os.getenv("APP_MODE", "local").lower()

    st.sidebar.title("Dashboard Mode")
    st.sidebar.write(f"Current mode: `{app_mode}`")

    if app_mode == "snowflake":
        st.sidebar.info("Reading analytics views from Snowflake.")
        data = load_snowflake_data()
    else:
        st.sidebar.info("Reading sample CSV files locally.")
        data = load_local_data()

    data = normalize_columns(data)
    render_dashboard(data)


if __name__ == "__main__":
    main()
