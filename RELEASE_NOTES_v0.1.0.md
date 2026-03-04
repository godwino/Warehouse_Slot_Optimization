## v0.1.0 - Initial Release

### Overview
Initial release of **HVDC Grocery Warehouse Digital Twin**, a Python + Streamlit simulation app for evaluating warehouse slotting strategies and their impact on picker travel and productivity.

### Included
- Synthetic warehouse data generation:
  - 1,000 SKUs (configurable), categories, velocity classes, dimensions, weight
  - Outbound order generation with velocity-weighted demand
  - Inbound truck arrival simulation (100 trucks configurable)
- Warehouse digital twin layout:
  - Aisles, bays, levels, and distance-to-pick-path modeling
- Slotting strategies:
  - Random slotting baseline
  - PRIME slotting (closest distance + ergonomic levels 2/3 for high-velocity SKUs)
- Picking simulation engine:
  - Travel distance estimation
  - Cases picked and cases-per-hour metrics
- Streamlit dashboard:
  - Run Simulation workflow
  - KPI summary
  - Warehouse layout visualization
  - Picker travel heatmap
  - Random vs PRIME comparison chart
  - Scenario comparison tab (baseline vs optimized)
  - CSV export buttons for key outputs
- Test coverage:
  - Unit tests for data generation, layout/slotting, picking, and truck simulation

### Tech Stack
- Python 3.11
- Pandas
- NumPy
- Plotly
- Streamlit
- unittest

### Validation
- Unit tests passing locally (`python -m unittest discover -s tests -p "test_*.py"`).
- Simulation smoke test confirms measurable travel reduction under PRIME slotting vs random baseline.

### Notes
This release is a **logic-based digital twin prototype** using synthetic data. It is designed for strategy evaluation and can be extended to production decision support by integrating WMS/ERP/order/labor data.
