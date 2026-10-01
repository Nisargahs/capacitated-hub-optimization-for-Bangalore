import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import KMeans

INPUT_FILE = "bangalore_customers.csv"

K = 20
CAPACITY = 2500
RANDOM_SEED = 42
MAX_ITERATIONS = 15


def load_data():
    df = pd.read_csv(INPUT_FILE)

    geometry = [
        Point(lon, lat)
        for lon, lat in zip(df["longitude"], df["latitude"])
    ]

    gdf = gpd.GeoDataFrame(
        df,
        geometry=geometry,
        crs="EPSG:4326"
    )

    gdf = gdf.to_crs("EPSG:32643")

    gdf["x"] = gdf.geometry.x
    gdf["y"] = gdf.geometry.y

    return gdf


def calculate_distances(points, centers):

    difference = (
        points[:, np.newaxis, :]
        - centers[np.newaxis, :, :]
    )

    distances = np.sqrt(
        np.sum(difference ** 2, axis=2)
    )

    return distances


def create_initial_hubs(points, weights):

    model = KMeans(
        n_clusters=K,
        random_state=RANDOM_SEED,
        n_init=10
    )

    model.fit(
        points,
        sample_weight=weights
    )

    return model.cluster_centers_


def capacity_constrained_assignment(distances):

    n_customers, n_hubs = distances.shape

    assignments = np.full(
        n_customers,
        -1,
        dtype=int
    )

    hub_counts = np.zeros(
        n_hubs,
        dtype=int
    )

    sorted_hubs = np.argsort(
        distances,
        axis=1
    )

    nearest = distances[
        np.arange(n_customers),
        sorted_hubs[:, 0]
    ]

    second_nearest = distances[
        np.arange(n_customers),
        sorted_hubs[:, 1]
    ]

    # Customers with a large difference between
    # first and second choice are more dependent
    # on their nearest hub.
    difficulty = second_nearest - nearest

    customer_order = np.argsort(
        -difficulty
    )

    for customer in customer_order:

        for hub in sorted_hubs[customer]:

            if hub_counts[hub] < CAPACITY:

                assignments[customer] = hub
                hub_counts[hub] += 1
                break

    return assignments, hub_counts


def calculate_weighted_centers(
    points,
    assignments,
    weights
):

    new_centers = np.zeros(
        (K, 2)
    )

    for hub in range(K):

        mask = assignments == hub

        if np.any(mask):

            hub_points = points[mask]
            hub_weights = weights[mask]

            new_centers[hub] = np.average(
                hub_points,
                axis=0,
                weights=hub_weights
            )

    return new_centers


def calculate_weighted_distance(
    distances,
    assignments,
    weights
):

    indices = np.arange(
        len(assignments)
    )

    assigned_distances = distances[
        indices,
        assignments
    ]

    return (
        np.sum(
            assigned_distances * weights
        )
        / np.sum(weights)
    )


def main():

    gdf = load_data()

    points = gdf[
        ["x", "y"]
    ].values

    weights = gdf[
        "order_volume"
    ].values

    print("Customers:", len(gdf))
    print(
        "Total order volume:",
        weights.sum()
    )
    print(
        "Number of hubs:",
        K
    )
    print(
        "Capacity per hub:",
        CAPACITY
    )
    print()

    print("Creating initial hub locations...")

    centers = create_initial_hubs(
        points,
        weights
    )

    best_distance = float("inf")
    best_assignments = None
    best_centers = None

    for iteration in range(1, MAX_ITERATIONS + 1):

        print(
            "\nIteration",
            iteration
        )

        # --------------------------------
        # 1. Calculate customer → hub distances
        # --------------------------------

        distances = calculate_distances(
            points,
            centers
        )

        # --------------------------------
        # 2. Capacity-constrained assignment
        # --------------------------------

        assignments, hub_counts = (
            capacity_constrained_assignment(
                distances
            )
        )

        # --------------------------------
        # 3. Validate
        # --------------------------------

        if np.any(assignments < 0):

            print("ERROR: Some customers unassigned.")
            break

        # --------------------------------
        # 4. Calculate objective
        # --------------------------------

        weighted_distance = (
            calculate_weighted_distance(
                distances,
                assignments,
                weights
            )
        )

        print(
            "Weighted average distance:",
            round(
                weighted_distance / 1000,
                3
            ),
            "km"
        )

        print(
            "Maximum hub size:",
            hub_counts.max()
        )

        # --------------------------------
        # 5. Save best solution
        # --------------------------------

        if weighted_distance < best_distance:

            best_distance = weighted_distance

            best_assignments = (
                assignments.copy()
            )

            best_centers = (
                centers.copy()
            )

            print("New best solution!")

        # --------------------------------
        # 6. Move hubs to weighted centroids
        # --------------------------------

        centers = calculate_weighted_centers(
            points,
            assignments,
            weights
        )

    # ====================================
    # Final validation
    # ====================================

    print("\n")
    print("FINAL SOLUTION")
    print("==============")

    print(
        "Customers:",
        len(gdf)
    )

    print(
        "Assigned:",
        np.sum(best_assignments >= 0)
    )

    print(
        "Weighted average distance:",
        round(
            best_distance / 1000,
            3
        ),
        "km"
    )

    final_counts = np.bincount(
        best_assignments,
        minlength=K
    )

    print(
        "Customers per hub:",
        final_counts.tolist()
    )

    print(
        "Maximum hub size:",
        final_counts.max()
    )

    print(
        "Capacity satisfied:",
        final_counts.max() <= CAPACITY
    )

    print(
        "Every customer assigned:",
        np.all(best_assignments >= 0)
    )

    # ====================================
    # Save customer assignments
    # ====================================

    output = gdf.drop(
        columns=["geometry"]
    ).copy()

    output["hub_id"] = (
        best_assignments + 1
    )

    output.to_csv(
        "customer_hub_assignments.csv",
        index=False
    )

    # ====================================
    # Save hub locations
    # ====================================

    hub_rows = []

    for hub in range(K):

        x, y = best_centers[hub]

        # Convert UTM coordinates back to lat/lon
        point = gpd.GeoSeries(
            [Point(x, y)],
            crs="EPSG:32643"
        ).to_crs("EPSG:4326").iloc[0]

        hub_rows.append({
            "hub_id": hub + 1,
            "latitude": point.y,
            "longitude": point.x,
            "customers": final_counts[hub]
        })

    hubs_df = pd.DataFrame(
        hub_rows
    )

    hubs_df.to_csv(
        "hub_locations.csv",
        index=False
    )

    print()
    print("Saved:")
    print("  customer_hub_assignments.csv")
    print("  hub_locations.csv")


if __name__ == "__main__":
    main()
