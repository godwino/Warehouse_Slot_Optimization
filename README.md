# Grocery slotting decision support

A local Streamlit application for QA to review grocery case positions within approved zones. Credit: Godwin Osayamwen.

## Run on Windows PowerShell

```powershell
cd C:\Users\Osayamwen\Desktop\Slot_Optimization\warehouse_digital_twin
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Open the localhost address printed by Streamlit. For an environment with dependencies already installed: `python -m streamlit run app/streamlit_app.py`.

```powershell
python -m unittest discover -s tests -v
python -m src.export_sample
```

The export command creates reproducible synthetic CSVs, blank templates and an infeasible example in `data/sample/`. The application also offers CSV downloads and atomic validated bundle imports. Use exact template headers, UTF-8, ISO dates and true/false booleans. Empty current locations denote unslotted products; order lines cannot reference an unslotted product.

## Workflow

1. Overview explains baseline/proposed metrics and assumptions.
2. Improve Existing Positions evaluates vacancies, swaps and bounded three-product cycles. Inspect current/proposed route maps and objective values.
3. Follow a Sample Assignment compares identical case quantities on the explicit route.
4. Place a New Product ranks vacancies and displacement chains, using expected frequency as a cold-start assumption.
5. QA Review saves an immutable scenario. Record reviewed before approved, with reviewer and notes. Approval does not execute moves.
6. Data and Validation supports searches, CSVs, scenario JSON and demo route configuration (01-48 or 11-58). Regenerating the demo replaces the active in-memory draft.
7. Stakeholder Brief provides a downloadable pilot outline.

SQLite snapshots and review history live in `data/scenarios.sqlite3`. Export/import scenario JSON includes data, configuration and proposed assignments; review history stays in the local database and is not imported as an approval. This is not enterprise authentication or a production approval system.

## Modules and retained features

`models`, `validation`, `sample_data`, `evaluation`, `optimization`, `movement`, and `persistence` separate the decision workflow. Original SKU generation, random/PRIME assignment, heatmaps and truck-arrival helpers remain available for legacy experiments. They are not the grocery constraint engine. Legacy picking now traverses each order by aisle rather than making one dock trip per line.

See [algorithm](docs/algorithm.md), [data dictionary](docs/data_dictionary.md) and [stakeholder brief / walkthrough / pilot](docs/stakeholder_brief.md).

## Limits

Heuristic search is bounded, not globally optimal. Existing-layout optimization performs at most three passes; three-cycles cover only the first twelve movable products. New-product search is capped at 10,000 location checks and configured displacement depth, so an infeasible result means none found within that search. No physical pallet simulation, layer packing, aggregate stacking-load proof, damage prediction, WMS/Vocollect integration, operational execution, enterprise identities or production approval controls are implemented. Shared rack-beam loads and geometric stock packing require measured data and a future model. Declared stock capacity is checked separately from upright case fit. Geometry/timing and synthetic case characteristics require local validation. Do not use illustrative load ratings as manufacturer specifications.
