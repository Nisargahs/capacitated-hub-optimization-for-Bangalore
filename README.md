Data Sources & Methodology
1. Bangalore Customer Location Proxy

Customer locations are synthetic proxy locations, generated from OSM residential building data for the Bangalore region.

Residential building geometries were extracted from OpenStreetMap.
Building centroids were used as proxy customer coordinates.
One proxy customer was generated per residential building feature.
Duplicate coordinates were removed.
Final dataset: 39,759 proxy customer locations.

These locations do not represent actual customer transactions or personally identifiable customer data.

2. Order Volume

Order-volume information was derived from the Online Shop 2024 dataset available on Kaggle.

The dataset contains customer orders and item quantities. Item quantities were aggregated at the customer level to obtain an order-volume distribution.

This distribution was then assigned to the 39,759 Bangalore proxy locations to create the synthetic demand dataset used by the optimization algorithm.

Final synthetic dataset:

Customers: 39,759
Total order volume: 373,160
Order volume per customer: 1–26 items

The resulting Bangalore demand dataset is synthetic. It combines geographic proxy locations from OpenStreetMap with an order-volume distribution from the Kaggle dataset.

3. Distance Calculation

Geographic coordinates were transformed from WGS84 (EPSG:4326) to UTM Zone 43N (EPSG:32643) so that Euclidean distances could be calculated in meters/kilometers.

4. Optimization

The objective is to minimize:
 \frac{\sum_{i} \omega_{i}d(i,h_{i})}{\sum_{i}\omega_{i}}
where:

\omega_{i} = order volume of customer \(i\)
$d(i,h_i)$ = distance from customer $i$ to its assigned hub
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
