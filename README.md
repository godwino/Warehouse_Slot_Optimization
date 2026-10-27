# Grocery Slot Intelligence

**Put the right case in the right place — and show the operational reasoning.**
A stakeholder demonstration by Godwin Osayamwen, built on the existing Warehouse Slot Optimization repository. Streamlit brings together grocery masters, constraint checks, route-aware recommendations, before/after evaluation and QA move plans. Existing simulation and legacy slotting modules remain available.

## Business problem

A physically compatible slot can still put fragile chips ahead of heavy water on the pick path. Incoming products also create displacement decisions: use a vacancy, relocate an incumbent, or rearrange several products? QA needs a clear, reviewable proposal that balances these trade-offs without overwriting occupied slots.

This demo supports that decision for D3 → D4 → D5. Pickers travel from low to high bay numbers in each aisle, then exit and start the next aisle. Rack level and eventual pallet layer are different concepts: earlier collection only creates an opportunity to build a stronger base.

## Run locally

```bash
git clone https://github.com/godwino/Warehouse_Slot_Optimization.git
cd Warehouse_Slot_Optimization
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py
```

```bash
python -m unittest discover -s tests -v
python -m src.export_sample
```

## Five-minute presentation

1. **Overview:** show the route map, product weights and baseline sequence risk. Hover over slots to inspect products.
2. **Improve Existing Positions:** run feasible improvement search; compare current and proposed positions and the objective.
3. **Follow a Sample Assignment:** show identical products and quantities collected in a different sequence.
4. **Place a New Product:** enter an incoming case. Try a light fragile case, a heavy robust case, and a 200 cm case that cannot fit. Inspect ranked options, score components and ordered moves.
5. **QA Review and Move Plan:** export a CSV action list or save a scenario for review. Local approval records a decision; it does not execute warehouse moves.

## How recommendations work

| Stage | Logic |
| --- | --- |
| Feasibility | Approved zone, upright dimensions with base rotation, allowed levels, case weight, declared stock capacity, rack load, replenishment permission and locks. |
| Case compatibility | Earlier-case crushability, support weakness, top-load exceedance and later-case footprint overhang contribute to a lower-is-better risk proxy. Weight and dimensions are case-level; cube is derived in m³. |
| Existing layout | Historical assignment co-occurrence weights pairwise route risk. Vacancies, swaps and bounded three-product cycles compete against relocation penalties and optional modeled travel. |
| Incoming case | Score = nearby compatibility + change in existing historical risk + frequency access cost + relocation penalty. Compatibility uses the eight nearest products in the approved zone as an explicit exposure assumption. |
| Frequency | Incoming access cost = 0.15 × min(1, expected 30-day line frequency / 100) × normalized route position. This is a tunable demo preference, not measured travel savings. |
| Move plan | Vacancies are used first; cycles require compatible empty staging. A plan that cannot be sequenced without overwriting occupancy is rejected. |

Incoming cases have no invented historical co-picks. Weight, footprint and height affect fit and pair compatibility; cube is descriptive, not an independent safety proof. Scores are heuristic costs, not damage probabilities. Lower total cost ranks first; detailed components expose trade-offs.

## Demonstration data and assumptions

The reproducible seed-42 pilot includes 63 SKUs, 144 slots and 30 days of synthetic assignments. Seven families cover vinegar, water, Pepsi, juice, Great Value cola, rice and chips. Family-specific dimensions and variant weights produce different cubes and support profiles. Frequency, visits/day and cases/day are calculated from the generated lines. These are illustrative cases and packaging ratings, not manufacturer specifications or company operational data. Use `data/sample/` CSVs and templates for imports; all three files are validated together.

## Expected operational value and pilot measurement

The intended value is more consistent QA decisions, fewer heavy-after-fragile collection patterns and transparent relocation effort. No savings or safety improvement has been established. Run a controlled pilot on comparable shifts and SKU mixes: measure damaged cases per 1,000 cases, damage dollars, cases per labour hour, replenishment effort, move execution time and QA acceptance. Compare the same workload before/after in this demo; validate any real benefit against observed results and implementation costs.

## Scope and limitations

Search is bounded, not globally optimal: existing optimization defaults to three passes with three-cycles limited to the first twelve movable SKUs. Incoming search allows configured displacement depth and at most 10,000 location checks; failure means no option found within those limits. Route-order stability summaries describe the master sequence, while historical sequence risk uses actual synthetic assignment co-occurrence. Neither is a physical pallet simulation.

The model does not prove cumulative stacking loads, layer packing, shared beam loads or aggregate geometric stock fit. Slot stock capacity is a declared input. WMS integration, authenticated approval and live execution are outside scope. SQLite scenarios (`data/scenarios.sqlite3`) use self-reported reviewer names. Incoming-case draft placement should be reviewed/exported before beginning another optimization; reset the demonstration for a fresh baseline.

See [algorithm details](docs/algorithm.md), [data dictionary](docs/data_dictionary.md) and [stakeholder pilot brief](docs/stakeholder_brief.md). Original generators, PRIME/random assignment, picking and truck helpers are preserved separately from the grocery engine.
