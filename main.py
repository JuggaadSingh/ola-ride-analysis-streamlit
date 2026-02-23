import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="OLA Ride Analysis",
    page_icon="🚕",
    layout="wide"
)

# Title
st.title("🚕 OLA Ride Data Analysis Dashboard")
st.markdown("### Internship Project | SQL + Power BI + Streamlit")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("OLA_DataSet - July.csv")
    return df

df = load_data()

# Show basic info
st.subheader("📄 Dataset Preview")
st.dataframe(df.head())

st.subheader("📊 Dataset Summary")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Rides", len(df))

with col2:
    st.metric("Unique Customers", df["Customer_ID"].nunique())

with col3:
    st.metric("Vehicle Types", df["Vehicle_Type"].nunique())

# Sidebar
st.sidebar.title("OLA Dashboard")
menu = st.sidebar.radio(
    "Navigate",
    ["Overall", "Vehicle Type", "Revenue", "Cancellation", "Ratings"]
)

# -------------------- OVERALL --------------------
if menu == "Overall":
    st.header("📊 Overall Ride Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rides", len(df))

    with col2:
        st.metric("Successful Rides", df[df["Booking_Status"] == "Success"].shape[0])

    with col3:
        st.metric("Cancelled Rides", df[df["Booking_Status"] != "Success"].shape[0])

# -------------------- VEHICLE TYPE --------------------
elif menu == "Vehicle Type":
    st.header("🚗 Vehicle Type Analysis")

    # Group by Vehicle Type
    vehicle_summary = df.groupby("Vehicle_Type").agg(
        Total_Booking_Value=("Booking_Value", "sum"),
        Success_Booking_Value=("Booking_Value", lambda x: x[df.loc[x.index, "Booking_Status"] == "Success"].sum()),
        Avg_Distance=("Ride_Distance", "mean"),
        Total_Distance=("Ride_Distance", "sum")
    ).reset_index()

    # Round values
    vehicle_summary["Avg_Distance"] = vehicle_summary["Avg_Distance"].round(2)

    # Show table
    st.subheader("📋 Vehicle-wise Performance Summary")
    st.dataframe(vehicle_summary, use_container_width=True)

    # Bar chart: Total Distance
    st.subheader("📊 Total Distance by Vehicle Type")
    st.bar_chart(
        vehicle_summary.set_index("Vehicle_Type")["Total_Distance"]
    )

# -------------------- REVENUE --------------------
elif menu == "Revenue":
    st.header("💰 Revenue Analysis")

    # Total Revenue
    total_revenue = df["Booking_Value"].sum()

    # Revenue from successful rides
    success_revenue = df[df["Booking_Status"] == "Success"]["Booking_Value"].sum()

    col1, col2 = st.columns(2)
    col1.metric("💵 Total Revenue", f"₹ {round(total_revenue, 2)}")
    col2.metric("✅ Successful Ride Revenue", f"₹ {round(success_revenue, 2)}")

    # Revenue by Payment Method
    st.subheader("📊 Revenue by Payment Method")

    payment_revenue = (
        df[df["Booking_Status"] == "Success"]
        .groupby("Payment_Method")["Booking_Value"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(payment_revenue)

# -------------------- CANCELLATION --------------------
elif menu == "Cancellation":
    st.header("❌ Cancellation Analysis")

    # Filter only cancelled rides
    cancelled_df = df[df["Booking_Status"] != "Success"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Cancelled Rides", cancelled_df.shape[0])

    with col2:
        st.metric(
            "Cancellation Rate (%)",
            round((cancelled_df.shape[0] / df.shape[0]) * 100, 2)
        )

    st.subheader("📊 Cancellation by Status")
    cancel_status = cancelled_df["Booking_Status"].value_counts()
    st.bar_chart(cancel_status)

    # If cancellation reason column exists
    if "Canceled_Rides_Reason" in df.columns:
        st.subheader("📌 Cancellation Reasons")
        cancel_reason = cancelled_df["Canceled_Rides_Reason"].value_counts()
        st.bar_chart(cancel_reason)
    else:
        st.info("Cancellation reason column not available in dataset.")

# -------------------- RATINGS --------------------
elif menu == "Ratings":
    st.header("⭐ Ratings Analysis")

    # Remove null ratings
    ratings_df = df.dropna(subset=["Driver_Ratings", "Customer_Ratings"])

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Driver Rating",
            round(ratings_df["Driver_Ratings"].mean(), 2)
        )

    with col2:
        st.metric(
            "Average Customer Rating",
            round(ratings_df["Customer_Ratings"].mean(), 2)
        )

    st.subheader("📊 Driver Ratings Distribution")
    st.bar_chart(ratings_df["Driver_Ratings"].value_counts().sort_index())

    st.subheader("📊 Customer Ratings by Vehicle Type")
    avg_customer_rating = (
        ratings_df.groupby("Vehicle_Type")["Customer_Ratings"]
        .mean()
        .sort_values(ascending=False)
    )
    st.bar_chart(avg_customer_rating)

    st.subheader("🔍 Customer vs Driver Ratings Relationship")
    st.scatter_chart(
        ratings_df[["Customer_Ratings", "Driver_Ratings"]]
    )