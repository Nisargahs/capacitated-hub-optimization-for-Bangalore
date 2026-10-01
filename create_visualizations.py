import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd


# ============================================================
# 1. K vs Weighted Average Distance
# ============================================================

results = pd.read_csv("k_comparison.csv")

plt.figure(figsize=(8, 5))

plt.plot(
    results["k"],
    results["weighted_avg_distance_km"],
    marker="o"
)

for _, row in results.iterrows():
    plt.annotate(
        "{:.3f} km".format(row["weighted_avg_distance_km"]),
        (row["k"], row["weighted_avg_distance_km"]),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center"
    )

plt.xlabel("Number of Hubs (k)")
plt.ylabel("Weighted Average Distance (km)")
plt.title("Hub Count vs Weighted Average Delivery Distance")
plt.xticks(results["k"])
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    "k_vs_distance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: k_vs_distance.png")


# ============================================================
# 2. Bangalore Customer-Hub Map
# ============================================================

customers = pd.read_csv(
    "customer_hub_assignments.csv"
)

hubs = pd.read_csv(
    "hub_locations.csv"
)

# Convert customer locations to GeoDataFrame
customer_geometry = gpd.points_from_xy(
    customers["longitude"],
    customers["latitude"]
)

customer_gdf = gpd.GeoDataFrame(
    customers,
    geometry=customer_geometry,
    crs="EPSG:4326"
)

# Convert hubs to GeoDataFrame
hub_geometry = gpd.points_from_xy(
    hubs["longitude"],
    hubs["latitude"]
)

hub_gdf = gpd.GeoDataFrame(
    hubs,
    geometry=hub_geometry,
    crs="EPSG:4326"
)


plt.figure(figsize=(10, 10))

# Customer locations
plt.scatter(
    customer_gdf["longitude"],
    customer_gdf["latitude"],
    s=1,
    alpha=0.15,
    label="Customer locations"
)

# Hub locations
plt.scatter(
    hub_gdf["longitude"],
    hub_gdf["latitude"],
    s=100,
    marker="^",
    edgecolors="black",
    linewidths=0.8,
    label="Optimized hubs"
)

# Hub labels
for _, hub in hub_gdf.iterrows():

    plt.annotate(
        "H{}".format(int(hub["hub_id"])),
        (
            hub["longitude"],
            hub["latitude"]
        ),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8,
        fontweight="bold"
    )


plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.title(
    "Optimized Micro-Fulfillment Hub Locations\n"
    "Bangalore - k = 20"
)

plt.legend()
plt.grid(True, alpha=0.2)
plt.tight_layout()

plt.savefig(
    "bangalore_hub_map.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: bangalore_hub_map.png")
