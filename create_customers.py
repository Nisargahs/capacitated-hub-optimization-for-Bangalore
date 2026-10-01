import geopandas as gpd
import pandas as pd

INPUT = "bangalore-residential.geojson"
OUTPUT = "customer_locations.csv"

# Read OSM residential buildings
gdf = gpd.read_file(INPUT)

# Keep genuine residential building polygons
gdf = gdf[
    gdf["building"].isin(["apartments", "house", "residential"])
].copy()

print(f"Residential buildings: {len(gdf)}")

# OSM data is in latitude/longitude.
# Project to a metric CRS before calculating centroids.
gdf = gdf.to_crs(epsg=32643)  # UTM Zone 43N, appropriate for Bangalore

# Calculate building centroids
gdf["centroid"] = gdf.geometry.centroid

# Convert centroids back to WGS84
centroids = gpd.GeoDataFrame(
    gdf[["building"]],
    geometry=gdf["centroid"],
    crs="EPSG:32643"
).to_crs(epsg=4326)

# Build customer-location dataset
customers = pd.DataFrame({
    "customer_id": [
        f"C{i:05d}" for i in range(1, len(centroids) + 1)
    ],
    "latitude": centroids.geometry.y,
    "longitude": centroids.geometry.x,
    "building_type": centroids["building"].values
})

customers.to_csv(OUTPUT, index=False)

print(f"Created {len(customers)} customer locations")
print(f"Saved to {OUTPUT}")
print(customers.head())
