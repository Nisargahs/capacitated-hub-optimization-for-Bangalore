import pandas as pd
import numpy as np

RANDOM_SEED = 42

# Bangalore customer locations derived from OSM
customers = pd.read_csv("customer_locations.csv")

# Reference online-shopping dataset
orders = pd.read_csv("online_shop/orders.csv")
items = pd.read_csv("online_shop/order_items.csv")

# Join orders to their item quantities
merged = orders.merge(items, on="order_id")

# Calculate total items ordered by each reference customer
reference_volume = (
    merged.groupby("customer_id")["quantity"]
    .sum()
    .values
)

# Reproduce the empirical distribution for all Bangalore customers
rng = np.random.default_rng(RANDOM_SEED)

n_customers = len(customers)

# Repeat the reference distribution enough times
repeated = np.resize(
    rng.permutation(reference_volume),
    n_customers
)

# Shuffle so repeated blocks aren't spatially correlated
rng.shuffle(repeated)

customers["order_volume"] = repeated.astype(int)

# Save final dataset
customers.to_csv("bangalore_customers.csv", index=False)

print(f"Reference customers: {len(reference_volume)}")
print(f"Bangalore customers: {len(customers)}")
print(f"Total order volume: {customers['order_volume'].sum():,}")
print("\nVolume statistics:")
print(customers["order_volume"].describe())

print("\nSaved to bangalore_customers.csv")
