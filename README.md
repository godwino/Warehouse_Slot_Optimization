# HVDC Grocery Warehouse Digital Twin

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![CI](https://github.com/godwino/Warehouse_Slot_Optimization/actions/workflows/ci.yml/badge.svg)](https://github.com/godwino/Warehouse_Slot_Optimization/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-unittest-green.svg)](./tests)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](./LICENSE)

Python + Streamlit digital twin simulation for a grocery distribution center, showing how PRIME SLOT slotting reduces picker travel distance versus random slotting.

## Suggested GitHub Description
Digital twin simulation for grocery DC slotting optimization: compares random vs PRIME slotting and quantifies picker travel and productivity impact.

## Why This Project
- Demonstrates slotting strategy impact before operational rollout.
- Provides an explainable baseline vs optimized comparison.
- Supports decision-making with reproducible simulation and KPI outputs.

## Features
- Synthetic data generation for 1,000 SKUs (configurable)
- 100 truck arrivals simulation (configurable)
- Warehouse layout with aisles, bays, and levels
- Slotting strategies:
  - Random slotting
  - PRIME slotting (closest travel + ergonomic levels 2/3)
- Picker travel simulation across outbound orders
- Streamlit dashboard with:
  - KPIs (distance, cases, CPH, distance saved)
  - Warehouse layout chart
  - Picker travel heatmap
  - Random vs PRIME comparison chart
  - Scenario Comparison tab (baseline vs optimized side-by-side)
  - CSV export buttons for key simulation outputs

## Project Structure
```text
warehouse_digital_twin/
|
|-- app/
|   |-- streamlit_app.py
|-- src/
|   |-- __init__.py
|   |-- generate_data.py
|   |-- warehouse_layout.py
|   |-- slotting_engine.py
|   |-- picking_simulation.py
|   `-- truck_simulation.py
|-- tests/
|   |-- test_generate_data.py
|   |-- test_layout_and_slotting.py
|   `-- test_picking_and_trucks.py
|-- requirements.txt
`-- README.md
```

## Local Setup
1. Create and activate a Python 3.11 virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app from project root:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Run Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

## GitHub Operations
- CI workflow: `.github/workflows/ci.yml`
- Changelog: `CHANGELOG.md`
- Contribution guide: `CONTRIBUTING.md`
- Roadmap: `ROADMAP.md`

## Notes on Reproducibility
- The app exposes a `Random Seed` sidebar control.
- Using the same seed and inputs reproduces the same simulation outputs.
