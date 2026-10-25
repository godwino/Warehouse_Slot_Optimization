# Data dictionary

CSV templates contain every dataclass field. IDs are text, numeric values must be finite. Required numeric capacities/dimensions are positive. Route index may be zero. Blank product location means unslotted. Boolean fields accept true/false.

| Entity | Fields | Meaning / units |
|---|---|---|
| Product | sku, description, category, zone | Unique identifier, readable description, category, approved zone |
| Product | weight_kg; length_cm, width_cm, height_cm | Case-level weight and upright dimensions; base may rotate 90 degrees |
| Product | volume_cm3 | Calculated length * width * height; property, not a CSV input or fit test |
| Product | packaging | Descriptive packaging type |
| Product | support, crushability | Illustrative QA ratings 0 to 1; greater means stronger support / greater vulnerability |
| Product | max_top_kg | Maximum single later case weight for proxy penalty; not full pallet cumulative-load proof |
| Product | location, locked | Current location ID; fixed SKU flag |
| Product | expected_frequency | Assumed new-product order-line count over comparable history window |
| Product | required_stock, allowed_levels | Required pick-face cases; allowed level numbers separated by vertical bars |
| Location | location_id, zone, aisle, bay, level | Unique location, approved zone and position |
| Location | route | Explicit unique sequence within zone, lower picked earlier |
| Location | length_cm, width_cm, height_cm | Usable case-level envelope |
| Location | case_weight_limit_kg | Maximum individual case weight |
| Location | stock_capacity, rack_load_limit_kg | Declared case count capacity and allocated location stock-load allowance; not shared beam proof |
| Location | locked, replenishment_allowed | Fixed slot; permission for a replenished face (required stock >1) |
| Order line | date, order_id, assignment_id | ISO date, business order, distinct zone pallet assignment |
| Order line | sku, qty, zone | Product ID, positive integer case count, assignment zone |
| Derived | line_frequency, case_velocity | Observed line count and case sum across the supplied history window |
| Derived | occupied / empty | Derived from assignment occupancy, never maintained independently |

Scenario JSON contains version, products, locations, orders, config and proposed assignment map. Config includes aisle order, bay bounds, geometry, timing and objective weights. SQLite retains immutable scenario payloads plus append-only review events with self-reported reviewer, notes and UTC time. No roles or authentication are implied.
