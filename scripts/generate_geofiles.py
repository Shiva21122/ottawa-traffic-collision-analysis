

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import zipfile
import os

# Step 1: Load your original CSV
csv_path = "data/processed/Cleaned_Traffic_Data.csv"  # <-- Update this if needed
df = pd.read_csv(csv_path)

# Step 2: Create WGS84 and Projected geometries
gdf_wgs = gpd.GeoDataFrame(df.copy(),
    geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
    crs="EPSG:4326"
)
gdf_proj = gpd.GeoDataFrame(df.copy(),
    geometry=[Point(x, y) for x, y in zip(df['x_x'], df['y_x'])],
    crs="EPSG:32618"
)

# Step 3: Add geometry columns to main DataFrame
df['geometry_latlon'] = gdf_wgs.geometry.astype(str)
df['geometry_projected'] = gdf_proj.geometry.astype(str)

# Step 4: Save full version as CSV then ZIP it
full_csv = "Cleaned_Traffic_Data_with_geometry.csv"
df.to_csv(full_csv, index=False)

zip_path = "Cleaned_Traffic_Data_with_geometry.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(full_csv)
print(f"Zipped full file: {zip_path}")

# Optional: remove the large CSV to save space
os.remove(full_csv)

# Step 5: Save a sample version (first 5000 rows)
sample_csv = "Cleaned_Traffic_Data_sample.csv"
df.head(5000).to_csv(sample_csv, index=False)
print(f"Sample saved: {sample_csv}")
