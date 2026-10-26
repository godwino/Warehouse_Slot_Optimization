# Stable pallet builder for grocery pickers

A local Streamlit application for QA and warehouse teams to review case placement and build safer, more stable grocery pallets within approved zones. The primary goal is to help pickers assemble pallets that are stable, crush-resistant and more operationally safe, while still improving pick efficiency and decision quality. Credit: Godwin Osayamwen.

## Run on Windows PowerShell

```powershell
cd C:\Users\Osayamwen\Desktop\Slot_Optimization\warehouse_digital_twin
python -m venv .venv
\.\.venv\Scripts\python.exe -m pip install -r requirements.txt
\.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Open the localhost address printed by Streamlit. For an environment with dependencies already installed: `python -m streamlit run app/streamlit_app.py`.

```powershell
python -m unittest discover -s tests -v
python -m src.export_sample
```

The export command creates reproducible synthetic CSVs, blank templates and an infeasible example in `data/sample/`. The application also offers CSV downloads and atomic validated bundle imports. Use exact template headers, UTF-8, ISO dates and true/false booleans. Empty current locations denote unslotted products; order lines cannot reference an unslotted product.

## Workflow

1. Overview explains the current baseline, proposed pallet-support metrics and the assumptions behind stable case placement.
2. Decision-tree recommendation helps you enter product size, weight, support and crushability, then ranks the best warehouse slot options using practical fit and stability logic.
3. Improve Existing Positions evaluates vacancies, swaps and bounded three-product cycles. Inspect current/proposed route maps and objective values with a focus on case compatibility and stable pallet construction.
4. Follow a Sample Assignment compares identical case quantities on the explicit route and highlights support/crushability trade-offs in pallet formation.
5. Place a New Product ranks vacancies and displacement chains using expected frequency as a cold-start assumption while checking whether a case can be safely integrated into stable pallet builds.
6. QA Review saves an immutable scenario. Record reviewed before approved, with reviewer and notes. Approval does not execute moves, but it does create a decision record for safe pallet build planning.
7. Data and Validation supports searches, CSVs, scenario JSON and demo route configuration (01-48 or 11-58). Regenerating the demo replaces the active in-memory draft.
8. Stakeholder Brief provides a downloadable pilot outline focused on pallet stability and picker safety.

SQLite snapshots and review history live in `data/scenarios.sqlite3`. Export/import scenario JSON includes data, configuration and proposed assignments; review history stays in the local database and is not imported as an approval. This is not enterprise authentication or a production approval system.

## Modules and retained features

`models`, `validation`, `sample_data`, `evaluation`, `optimization`, `movement`, and `persistence` separate the decision workflow. Original SKU generation, random/PRIME assignment, heatmaps and truck-arrival helpers remain available for legacy experiments. They are not the grocery constraint engine. Legacy picking now traverses each order by aisle rather than making one dock trip per line.

The new “Place a New Product” workflow behaves like a guided decision tree: users enter case weight, dimensions, support, crushability, allowed levels and other slotting inputs, and the app recommends the best compatible slot while showing the reasoning path and candidate moves.

See [algorithm](docs/algorithm.md), [data dictionary](docs/data_dictionary.md) and [stakeholder brief / walkthrough / pilot](docs/stakeholder_brief.md).

## Limits

Heuristic search is bounded, not globally optimal. Existing-layout optimization performs at most three passes; three-cycles cover only the first twelve movable products. New-product search is capped at 10,000 location checks and configured displacement depth, so an infeasible result means none found within that search. No physical pallet simulation, layer packing, aggregate stacking-load proof, damage prediction, WMS/Vocollect integration, operational execution, enterprise identities or production approval controls are implemented. Shared rack-beam loads and geometric stock packing require measured data and a future model. Declared stock capacity is checked separately from upright case fit. Geometry/timing and synthetic case characteristics require local validation. Do not use illustrative load ratings as manufacturer specifications.
