import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import KMeans

INPUT_FILE = "bangalore_customers.csv"

K_VALUES = [16, 18, 20, 22, 24]
K = 16
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

    global K

    gdf = load_data()

    points = gdf[["x", "y"]].values
    weights = gdf["order_volume"].values

    print("Customers:", len(gdf))
    print("Total order volume:", weights.sum())
    print()

    results = []

    for k in K_VALUES:

        K = k

        print("=" * 50)
        print("Running K =", K)
        print("=" * 50)

        # Create initial hubs
        centers = create_initial_hubs(
            points,
            weights
        )

        best_distance = float("inf")
        best_assignments = None
        best_centers = None

        # Same iterative optimization used in our
        # working K=16 solution
        for iteration in range(15):

            distances = calculate_distances(
                points,
                centers
            )

            assignments, hub_counts = (
                capacity_constrained_assignment(
                    distances
                )
            )

            if np.any(assignments < 0):
                print("ERROR: Some customers unassigned.")
                break

            weighted_distance = (
                calculate_weighted_distance(
                    distances,
                    assignments,
                    weights
                )
            )

            if weighted_distance < best_distance:

                best_distance = weighted_distance

                best_assignments = (
                    assignments.copy()
                )

                best_centers = (
                    centers.copy()
                )

            centers = calculate_weighted_centers(
                points,
                assignments,
                weights
            )

        final_counts = np.bincount(
            best_assignments,
            minlength=K
        )

        avg_distance_km = (
            best_distance / 1000
        )

        feasible = (
            np.all(final_counts <= CAPACITY)
            and
            np.all(best_assignments >= 0)
        )

        print(
            "Weighted average distance:",
            round(avg_distance_km, 3),
            "km"
        )

        print(
            "Maximum hub size:",
            final_counts.max()
        )

        print(
            "Capacity satisfied:",
            feasible
        )

        results.append({
            "k": K,
            "weighted_avg_distance_km":
                avg_distance_km,
            "max_customers_per_hub":
                final_counts.max(),
            "feasible":
                feasible
        })

    results_df = pd.DataFrame(results)

    print()
    print("FINAL COMPARISON")
    print("================")

    print(
        results_df.to_string(index=False)
    )

    results_df.to_csv(
        "k_comparison.csv",
        index=False
    )

    print()
    print("Saved: k_comparison.csv")


if __name__ == "__main__":
    main()
