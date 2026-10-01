## Python Packages

The project uses the following Python packages:
======================================================================================================================================== 
| `pandas` | Reading, cleaning, transforming, and aggregating customer and order-volume data stored in CSV files. |
| `numpy` | Numerical operations and array-based calculations used during data processing and optimization. |
| `geopandas` | Reading and processing the OpenStreetMap-derived GeoJSON containing residential building geometries. |
| `shapely` | Working with geometric objects and calculating building centroids to generate proxy customer locations. |
| `scikit-learn` | Provides the weighted K-Means implementation used to generate the initial hub locations. |
| `matplotlib` | Creating the hub-location map and the hub-count vs. weighted-average-distance visualization.
============================================================================================================================================

|Data Sources & Methodology

1. Bangalore Customer Location Proxy

Customer locations are synthetic proxy locations, generated from OSM residential building data for the Bangalore region.

Residential building geometries were extracted from OpenStreetMap.
Building centroids were used as proxy customer coordinates.
One proxy customer was generated per residential building feature.
Duplicate coordinates were removed.
Final dataset: 39,759 proxy customer locations.

These locations do not represent actual customer transactions or personally identifiable customer data.

 `create_customers.py` -> Generates proxy customer locations from residential building geometries. 
 `add_order_volume.py` -> Adds order-volume values to the Bangalore proxy customers. 

2. Order Volume

Order-volume information was derived from the Online Shop 2024 dataset available on Kaggle.

The dataset contains customer orders and item quantities. Item quantities were aggregated at the customer level to obtain an order-volume distribution.

This distribution was then assigned to the 39,759 Bangalore proxy locations to create the synthetic demand dataset used by the optimization algorithm.

Final  dataset:

Customers: 39,759
Total order volume: 373,160
Order volume per customer: 1–26 items

The resulting Bangalore demand dataset is synthetic. It combines geographic proxy locations from OpenStreetMap with an order-volume distribution from the Kaggle dataset.

3. Distance Calculation

Geographic coordinates were transformed from WGS84 (EPSG:4326) to UTM Zone 43N (EPSG:32643) so that Euclidean distances could be calculated in meters/kilometers.

4. Optimization

The objective is to minimize:
Weighted Average Distance = (Σᵢ ωᵢ d(i,hᵢ)) / (Σᵢ ωᵢ)
where:

- $\omega_i$ = order volume of customer $i$
- $d(i,h_i)$ = distance from customer $i$ to its assigned hub
- $h_i$ = hub assigned to customer $i$

Each customer is assigned to exactly one hub, with a maximum of 2,500 customers per hub.

The solution uses:

Weighted K-Means for initial hub placement
Capacity-constrained customer assignment
Order-volume-weighted hub-centroid recalculation
Iterative refinement

The approach is a heuristic capacitated clustering method, not an exact global optimization algorithm.

5. Data Sources
OpenStreetMap — residential building geometry used to generate geographic proxy locations.
Kaggle – Online Shop 2024 — used to derive the synthetic order-volume distribution.


## Project Structure

| File | Description |

 `constraint_hubs.py` ->  Main optimization script for the selected 20-hub solution. 
 `compare_k.py` -> Evaluates different hub counts (`k = 16, 18, 20, 22, 24`). 
 `create_visualizations.py` -> Generates the project visualizations. 
 
 `bangalore_customers.csv`  Final synthetic customer dataset with coordinates and order volume. 
 `customer_hub_assignments.csv`->| Customer-to-hub assignment results. 
 `hub_locations.csv` -> Locations and customer counts of the selected hubs. 
 `k_comparison.csv` -> Comparison of results for different values of `k`.

 Results:
 `bangalore_hub_map.png` -> Map showing proxy customer locations and optimized hubs. 
 `k_vs_distance.png` -> Plot showing weighted average distance for different hub counts. 

output of Constraints_hubs.py -> Customers: 39759
Total order volume: 373160
Number of hubs: 20
Capacity per hub: 2500

Creating initial hub locations...

Iteration 1
Weighted average distance: 2.321 km
Maximum hub size: 2500
New best solution!

Iteration 2
Weighted average distance: 2.134 km
Maximum hub size: 2500
New best solution!

Iteration 3
Weighted average distance: 2.097 km
Maximum hub size: 2500
New best solution!

Iteration 4
Weighted average distance: 2.082 km
Maximum hub size: 2500
New best solution!

Iteration 5
Weighted average distance: 2.081 km
Maximum hub size: 2500
New best solution!

Iteration 6
Weighted average distance: 2.089 km
Maximum hub size: 2500

Iteration 7
Weighted average distance: 2.085 km
Maximum hub size: 2500

Iteration 8
Weighted average distance: 2.089 km
Maximum hub size: 2500

Iteration 9
Weighted average distance: 2.095 km
Maximum hub size: 2500

Iteration 10
Weighted average distance: 2.093 km
Maximum hub size: 2500

Iteration 11
Weighted average distance: 2.094 km
Maximum hub size: 2500

Iteration 12
Weighted average distance: 2.093 km
Maximum hub size: 2500

Iteration 13
Weighted average distance: 2.093 km
Maximum hub size: 2500

Iteration 14
Weighted average distance: 2.093 km
Maximum hub size: 2500

Iteration 15
Weighted average distance: 2.093 km
Maximum hub size: 2500


FINAL SOLUTION
==============
Customers: 39759
Assigned: 39759
Weighted average distance: 2.081 km
Customers per hub: [2500, 1889, 2500, 2500, 2500, 1369, 2500, 723, 2500, 1029, 2500, 2500, 1697, 1868, 1763, 365, 1766, 2290, 2500, 2500]
Maximum hub size: 2500
Capacity satisfied: True
Every customer assigned: True

Saved:
  customer_hub_assignments.csv
  hub_locations.csv
