"""
Ottawa Traffic Collision Analysis - Data Cleaning
Business Question: Where and when do severe traffic collisions occur in Ottawa
(2017-2022), and which road/light/weather conditions drive severity?
Research: City of Ottawa Open Data - traffic collision records + 2019 location file.
Data Types: dates/times (parsed to datetime), categorical conditions (text),
geographic coordinates (float), collision counts (int).
Cleaning: standardize column names, parse dates/times, fill missing categorical
values with 'Unknown', drop columns >85% null, feature-engineer hour/day/month/year.
Output: data/processed/Cleaned_Joined_Traffic_Data.csv
Run from project root: python scripts/data_cleaning.py
"""
import pandas as pd
import numpy as np
import os

 
#Step 1: Load CSV Files Safely
 
detailed_path = "data/raw/Traffic_Collision_Data.csv"
location_path = "data/raw/Traffic_Collision_by_Location_2019.csv"

#Check if files exist
if not os.path.exists(detailed_path) or not os.path.exists(location_path):
    raise FileNotFoundError("❌ One or both CSV files not found. Please check file paths.")

#Load datasets
df_detailed = pd.read_csv(detailed_path)
df_location = pd.read_csv(location_path)

 
#Step 2: Standardize Column Names
 
df_detailed.columns = df_detailed.columns.str.strip().str.lower()
df_location.columns = df_location.columns.str.strip().str.lower()

 
#Step 3: Convert Date and Time Columns
 
df_detailed['accident_date'] = pd.to_datetime(df_detailed['accident_date'], errors='coerce')

if 'accident_time' in df_detailed.columns:
    df_detailed['accident_time'] = pd.to_datetime(df_detailed['accident_time'], format='%H:%M:%S', errors='coerce').dt.time
else:
    print("Column 'accident_time' not found. Time-based features will be skipped.")

 
#Step 4: Fill Missing Values
 
for col in ['light', 'road_surface_condition', 'environment_condition']:
    if col in df_detailed.columns:
        df_detailed[col] = df_detailed[col].fillna('Unknown')

#Drop columns with >85% missing values
null_threshold = 0.85
null_pct = df_detailed.isnull().mean()
drop_cols = null_pct[null_pct > null_threshold].index
df_detailed.drop(columns=drop_cols, inplace=True)

 
#Step 5: Feature Engineering
 
if 'accident_time' in df_detailed.columns:
    df_detailed['hour'] = pd.to_datetime(df_detailed['accident_time'], errors='coerce').apply(lambda x: x.hour if pd.notnull(x) else np.nan)

df_detailed['day_of_week'] = df_detailed['accident_date'].dt.day_name()
df_detailed['month'] = df_detailed['accident_date'].dt.month_name()
df_detailed['year'] = df_detailed['accident_date'].dt.year

 
#Step 6: Clean Location Fields
 
df_detailed['location'] = df_detailed['location'].astype(str).str.strip().str.upper()
df_location['location'] = df_location['location'].astype(str).str.strip().str.upper()

 
#Step 7: Drop Duplicates
 
df_detailed.drop_duplicates(inplace=True)
df_location.drop_duplicates(inplace=True)

 
#Step 8: Merge Datasets on 'location'
 
df_merged = pd.merge(df_detailed, df_location, how='left', on='location')

 
#Step 9: Save Result
 
output_path = "data/processed/Cleaned_Joined_Traffic_Data.csv"
df_merged.to_csv(output_path, index=False)
print(f"Cleaned and joined data saved as: {output_path}")
