# Zone 1 slotting pilot

Credit: Godwin Osayamwen

Products already have approved zones. Some vulnerable cases are collected before suitable supporting cases, making pallet building difficult. QA needs explainable placement decisions, not automatic warehouse changes.

The application checks case fit and zoning, evaluates historical assignment co-occurrence, suggests moves and stages cycles safely. A reproducible synthetic example contains 63 vinegar, water, Pepsi, juice, Great Value cola, rice and chips products across D3-D5, empty faces, locked products and 30 days of assignments. Data are illustrative, not product specifications.

## Demo walkthrough

1. Open Overview and inspect the shared workload fingerprint and assumptions.
2. Improve Existing Positions, run the heuristic, and inspect current/proposed aisle maps including EMPTY and locked indicators.
3. Follow a Sample Assignment: compare the same cases in route order. Explain packaging/support trade-offs using the proxy definition.
4. Place a New Product. Try a normal case, then an oversized 200 cm case. Compare direct placement and displacement depth. Expected frequency is a cold-start assumption.
5. Save an immutable draft; inspect source/destination/dependencies, record reviewed and then approved with notes. Download the action list. No warehouse action is executed.
6. Export scenario JSON and CSVs; import a deliberately duplicated ID to demonstrate actionable rejection without replacing current data.

## Evidence and limits

Compare proxy score, moved products, affected orders, constraints and illustrative travel on identical orders. These establish model behavior only. Physical pallet stability, safety, damage and productivity outcomes remain unvalidated. All case ratings, stock capacity and distances require QA measurement. The heuristic is bounded and may miss feasible or better solutions. Approval is a local decision record, not an enterprise control.

## Proposed pilot

Before changes, collect a representative two-week baseline and agree definitions with QA and operations: rebuilds per completed pallet, damage incidents per 1,000 shipped cases, assignment picking minutes and replenishment labor minutes/cases. Record SKU mix, assignment case count, picker, shift, zone, promotions and exposure. Attribute damage consistently through shipping, and distinguish pre-existing damage.

Measure slot/rack limits, packaging ratings, walking routes, replenishment constraints and assignment IDs first. QA signs off measured fit, safe staging and move instructions; operations schedules any physical moves separately. Start with a small reversible set in Zone 1 and retain a rollback layout. Use matched shifts/assignments or a controlled crossover with comparable case mix; avoid comparing different workloads as if layout caused the difference. Collect the same measures over at least two post-change weeks and track exceptions and replenishment burden. Report denominators, sample sizes, uncertainty and confounders; extend observation for sparse damage events. Agree operational stop criteria with site management before the pilot. Do not claim causal savings or damage reduction from synthetic proxy scores.
