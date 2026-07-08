"""
Ottawa Traffic Collision Dashboard (Streamlit)
Interactive dashboard over the cleaned star-schema data (fact + 8 dimension tables).
Run from project root: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import logging

# Configure logging
logging.basicConfig(
    filename="app_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

st.set_page_config(page_title="Ottawa Traffic Dashboard 2017-2022", layout="wide")

# Load data
@st.cache_data
def load_data():
    try:
        fact_df = pd.read_csv("data/processed/Cleaned_Traffic_Data.csv", parse_dates=["accident_date"])
        dim_data = pd.read_excel("data/processed/Dimtables.xlsx", sheet_name=None)

        # Merge with dimension tables
        fact_df = fact_df.merge(dim_data['Dimlocation_type'], on="location_type_id", how="left")
        fact_df = fact_df.merge(dim_data['Dimclassification_of_accident'], on="Classificationid", how="left")
        fact_df = fact_df.merge(dim_data['Diminitial_impact_type'], on="impactid", how="left")
        fact_df = fact_df.merge(dim_data['Dimroad_surface_condition'], on="road_conditionid", how="left")
        fact_df = fact_df.merge(dim_data['Dimenvironment_condition'], on="environmentid", how="left")
        fact_df = fact_df.merge(dim_data['Dimlight'], on="lightid", how="left")
        fact_df = fact_df.merge(dim_data['Dimtraffic_control'], on="trafficid", how="left")
        fact_df = fact_df.merge(dim_data['Dimmax_injury'], on="injuryid", how="left")

        logging.info("Data loaded and merged successfully.")
        return fact_df, dim_data

    except Exception as e:
        logging.error(f"Error loading data: {e}")
        st.error("Failed to load data. Please check the log file for details.")
        return pd.DataFrame(), {}

# Load
df, dim_data = load_data()

if df.empty:
    st.stop()

st.title("Ottawa Traffic Collision Dashboard")

#Shared Filters
try:
    st.sidebar.header("Filter Data (Global)")
    years = sorted(df['accident_date'].dt.year.dropna().unique())
    days = sorted(df['weekday'].dropna().unique())
    locations = sorted(df['location_type'].dropna().unique())
    lights = sorted(df['light'].dropna().unique())
    impacts = sorted(df['initial_impact_type'].dropna().unique())

    selected_years = st.sidebar.multiselect("Year", years)
    selected_days = st.sidebar.multiselect("Day of Week", days)
    selected_locations = st.sidebar.multiselect("Location Type", locations)
    selected_lights = st.sidebar.multiselect("Light Condition", lights)
    selected_impacts = st.sidebar.multiselect("Impact Type", impacts)

    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df['accident_date'].dt.year.isin(selected_years)]
    if selected_days:
        filtered_df = filtered_df[filtered_df['weekday'].isin(selected_days)]
    if selected_locations:
        filtered_df = filtered_df[filtered_df['location_type'].isin(selected_locations)]
    if selected_lights:
        filtered_df = filtered_df[filtered_df['light'].isin(selected_lights)]
    if selected_impacts:
        filtered_df = filtered_df[filtered_df['initial_impact_type'].isin(selected_impacts)]
except Exception as e:
    logging.error(f"Error in filter processing: {e}")
    st.error("An error occurred while filtering data.")

# KPIs
try:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Collisions", f"{len(filtered_df):,}")
    col2.metric("Total Injuries", int(filtered_df['num_of_injuries'].fillna(0).sum()))
    col3.metric("Pedestrian Involved", int((filtered_df['num_of_pedestrians'] > 0).sum()))
    col4.metric("Vehicles Involved", int(filtered_df['num_of_vehicle'].fillna(0).sum()))

    if filtered_df['num_of_injuries'].sum() > 200:
        st.error("High Injury Alert: More than 200 injuries in filtered data!")
    elif len(filtered_df) > 1000:
        st.warning("High Volume: More than 1,000 collisions!")
except Exception as e:
    logging.warning(f"KPI rendering issue: {e}")

#Visualizations
try:
    st.subheader("Monthly Collision Trend")
    monthly = filtered_df.groupby(filtered_df['accident_date'].dt.to_period("M")).size().reset_index(name="Collisions")
    monthly['accident_date'] = monthly['accident_date'].astype(str)
    fig_line = px.line(monthly, x="accident_date", y="Collisions", title="Collisions Over Time")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Collisions by Day of Week")
    weekday_counts = filtered_df['weekday'].value_counts().reindex([
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ]).reset_index()
    weekday_counts.columns = ["Weekday", "Count"]
    fig_bar = px.bar(weekday_counts, x="Weekday", y="Count", title="Collisions by Weekday", color="Weekday")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Collision Map")
    st.markdown("Use filters below to customize the collision map view independently.")
    map_year = st.multiselect("Map - Year", years)
    map_location = st.multiselect("Map - Location Type", locations)
    map_light = st.multiselect("Map - Light Condition", lights)

    map_df = df.copy()
    if map_year:
        map_df = map_df[map_df['accident_date'].dt.year.isin(map_year)]
    if map_location:
        map_df = map_df[map_df['location_type'].isin(map_location)]
    if map_light:
        map_df = map_df[map_df['light'].isin(map_light)]

    map_df = map_df.dropna(subset=["lat", "long"]).copy()
    map_df.rename(columns={"long": "longitude"}, inplace=True)
    if not map_df.empty:
        st.map(map_df[["lat", "longitude"]])
    else:
        st.warning("No location data available after filtering.")

    st.subheader("Accident Classification")
    impact_count = filtered_df['classification_of_accident'].value_counts().reset_index()
    impact_count.columns = ['Classification', 'Count']
    fig_pie = px.pie(impact_count, names='Classification', values='Count', title='Accident Classification Breakdown')
    st.plotly_chart(fig_pie, use_container_width=True)
except Exception as e:
    logging.error(f"Visualization error: {e}")
    st.error("Failed to render some visualizations.")

#Insight Summary
try:
    st.subheader("Key Conditions Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        top_day = filtered_df['weekday'].mode()[0] if not filtered_df.empty else "N/A"
        st.metric("Most Frequent Day", top_day)
    with col2:
        top_light = filtered_df['light'].mode()[0] if not filtered_df.empty else "N/A"
        st.metric("Most Common Light Condition", top_light)
    with col3:
        top_surface = filtered_df['road_surface_condition'].mode()[0] if not filtered_df.empty else "N/A"
        st.metric("Top Road Surface", top_surface)
except Exception as e:
    logging.warning(f"Insight summary error: {e}")

#Comparative Analysis
try:
    st.subheader("Comparative Metrics")
    all_avg_injury_rate = df['num_of_injuries'].sum() / len(df)
    filtered_avg_injury_rate = filtered_df['num_of_injuries'].sum() / len(filtered_df) if len(filtered_df) > 0 else 0
    injury_diff = filtered_avg_injury_rate - all_avg_injury_rate
    st.write(f"Injury Rate (Filtered): **{filtered_avg_injury_rate:.2f}**")
    st.write(f"Injury Rate (Overall): **{all_avg_injury_rate:.2f}**")
    if injury_diff > 0:
        st.success(f"🔺 Injury rate is **{injury_diff:.2f}** higher than average.")
    elif injury_diff < 0:
        st.warning(f"🔻 Injury rate is **{-injury_diff:.2f}** lower than average.")
    else:
        st.info("Injury rate matches the overall average.")
except Exception as e:
    logging.warning(f"Comparative metric issue: {e}")

#Raw Data Table
try:
    st.subheader("Filtered Collision Data")
    st.dataframe(filtered_df.reset_index(drop=True))
    st.download_button("Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_collisions.csv")

    st.subheader("Dimension Tables")
    for name, table in dim_data.items():
        st.markdown(f"**{name}**")
        st.dataframe(table)
        st.download_button(f"Download {name}.csv", data=table.to_csv(index=False), file_name=f"{name}.csv")
except Exception as e:
    logging.error(f"Error rendering final tables: {e}")
    st.error("Unable to show final tables or downloads.")
