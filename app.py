import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Dashboard (Bersih tanpa logo)
st.set_page_config(
    page_title="Indonesian E-Commerce Logistics Dashboard", layout="wide"
)

st.title("Indonesian E-Commerce Logistics & Customer Satisfaction Dashboard")
st.markdown(
    "Interactive analytics dashboard tracking delivery performance,"
    " on-time fulfillment rates, shipping costs, and customer satisfaction"
    " across Indonesian logistics networks."
)


# Fungsi untuk memuat dataset CSV
@st.cache_data
def load_logistics_data():
  filename = "indonesia_ecommerce_logistics.csv"
  if os.path.exists(filename):
    return pd.read_csv(filename)
  else:
    return pd.DataFrame()


df = load_logistics_data()

if df.empty:
  st.warning(
      "Dataset file (`indonesia_ecommerce_logistics.csv`) not found. Please"
      " ensure the CSV file is uploaded."
  )
else:
  # Sidebar Filters
  st.sidebar.header("Filter Options")

  providers = sorted(df["shipping_provider"].unique())
  selected_providers = st.sidebar.multiselect(
      "Select Logistics Providers:", options=providers, default=providers
  )

  delivery_types = sorted(df["delivery_type"].unique())
  selected_types = st.sidebar.multiselect(
      "Select Delivery Types:", options=delivery_types, default=delivery_types
  )

  statuses = sorted(df["delivery_status"].unique())
  selected_statuses = st.sidebar.multiselect(
      "Select Delivery Status:", options=statuses, default=statuses
  )

  # Filter DataFrame
  filtered_df = df[
      (df["shipping_provider"].isin(selected_providers))
      & (df["delivery_type"].isin(selected_types))
      & (df["delivery_status"].isin(selected_statuses))
  ]

  # Executive Metrics Overview
  st.subheader("Executive Summary Metrics")
  col1, col2, col3, col4 = st.columns(4)

  total_shipments = len(filtered_df)
  ontime_count = len(filtered_df[filtered_df["delivery_status"] == "On-Time"])
  ontime_rate = (
      (ontime_count / total_shipments) * 100 if total_shipments > 0 else 0
  )
  avg_cost = (
      filtered_df["shipping_cost_idr"].mean() if not filtered_df.empty else 0
  )
  avg_rating = (
      filtered_df["customer_satisfaction_rating"].mean()
      if not filtered_df.empty
      else 0
  )

  with col1:
    st.metric(label="Total Shipments Tracked", value=f"{total_shipments:,}")
  with col2:
    st.metric(label="On-Time Delivery Rate", value=f"{ontime_rate:.1f}%")
  with col3:
    st.metric(label="Avg. Shipping Cost", value=f"Rp {avg_cost:,.0f}")
  with col4:
    st.metric(label="Avg. Customer Rating", value=f"⭐ {avg_rating:.2f} / 5.0")

  st.markdown("---")

  # Visualizations Layout
  col_a, col_b = st.columns(2)

  with col_a:
    st.subheader("Shipments by Logistics Provider")
    if not filtered_df.empty:
      prov_counts = (
          filtered_df["shipping_provider"].value_counts().reset_index()
      )
      prov_counts.columns = ["Provider", "Count"]
      fig_prov = px.bar(
          prov_counts,
          x="Provider",
          y="Count",
          color="Provider",
          title="Total Shipments per Provider",
          labels={"Provider": "Logistics Provider", "Count": "Shipment Count"},
      )
      st.plotly_chart(fig_prov, use_container_width=True)

  with col_b:
    st.subheader("Delivery Status Breakdown")
    if not filtered_df.empty:
      status_counts = filtered_df["delivery_status"].value_counts().reset_index()
      status_counts.columns = ["Status", "Count"]
      fig_status = px.pie(
          status_counts,
          names="Status",
          values="Count",
          title="Proportion of On-Time vs Delayed",
          hole=0.4,
      )
      st.plotly_chart(fig_status, use_container_width=True)

  # Scatter / Box Analysis
  st.subheader("Shipping Cost vs Customer Satisfaction Rating")
  if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x="shipping_cost_idr",
        y="customer_satisfaction_rating",
        color="delivery_type",
        symbol="delivery_status",
        title="Impact of Shipping Cost on Customer Rating",
        labels={
            "shipping_cost_idr": "Shipping Cost (IDR)",
            "customer_satisfaction_rating": "Satisfaction Rating",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

  # Raw Data Expander
  with st.expander("View Raw Logistics Dataset"):
    st.dataframe(df, use_container_width=True)
