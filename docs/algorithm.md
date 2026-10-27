# Algorithm and audit

Each assignment stays in one approved zone. Order ID is a customer/business order; date + assignment ID identifies a pallet picking workload. Multiple assignments may belong to one order. Route order is explicit and unique per zone; default D3, D4, D5 and ascending locations are configurable demo assumptions.

## Proxy definition

For every unordered pair of different SKUs in an assignment, weight their directional cost by the smaller case quantity. The earlier case E and later case L incur:

`crushability(E)*weight(L)/30 + (1-support(E))*support(L) + max(0,weight(L)-max_top_kg(E))/30 + max(0,base_area(L)-base_area(E))/3000`.

The sequence proxy is the weighted mean across all assignments. Lower is preferred. Co-occurrence is derived only from supplied assignment lines. This pairwise proxy ignores actual layering, cumulative loads, interlocking, orientation, wrap and driving forces. It neither proves stability nor predicts damage. Heavy-first alone is insufficient.

Existing-layout objective = proxy + move penalty * number of products moved from baseline + travel weight * illustrative travel meters / number of order lines. Defaults: 0.002 per move and zero travel weight. Best feasible improving vacancy moves, swaps and bounded three-cycles are searched for up to three passes. Candidates must have a safe staging plan. No optimality guarantee; no OR-Tools dependency. No-improvement is an explicit outcome.

New products: enumerate compatible locations and recursively displace occupants toward vacancies (up to selected depth, at most 10,000 location checks). Rank = move penalty * existing moves + expected line frequency * route index / 10,000. This is a transparent cold-start preference for earlier routes, not evidence of pallet sequence improvement. It does not invent co-occurrence for a new SKU. Ranking can favor relocations when the assumed frequency outweighs their penalty. Search order and bounds can omit feasible options.

## Hard checks

Zone, upright dimensions (base rotation only), case weight limit, allowed levels, unique occupancy, locked products/source/destination, declared stock count capacity, declared rack-load limit for required stock and replenishment permission. Case volume is calculated for information only. Stock capacity is supplied, not inferred by dividing volumes; beam/shared rack loads are outside scope. `max_top_kg` is a sequence proxy input, not a verified cumulative stacking constraint.

Move plans drain available destinations first. Cycles require an empty, unlocked compatible slot for temporary staging; each action depends conservatively on the previous action. No overwrite is permitted. A failed plan is flagged and its partial actions must not be executed. Draft -> reviewed -> approved/rejected records are stored with UTC timestamps against immutable snapshots. Approved/rejected records are terminal; save a fresh draft for revision.

## Evaluation and known-code audit

Baseline and proposal are evaluated against exactly the same order lines and SHA-256 workload fingerprint. Travel starts/ends at the front of the first configured aisle, uses front-entry/front-exit at each visited aisle, visits ascending bay numbers, and traverses the front cross-aisle between aisles. Bay positions and aisle gaps are configurable illustrative meters. Aisles are not assumed to be serpentine. Empty aisles have no depth traversal. Modeled cases/hour = cases * 3600 / (travel/walking speed + cases*handling seconds). Defaults 1.2 m/s and 5 s/case are visible assumptions, not productivity evidence.

The original code ignored dimensions/weight and zones, had no packaging model, made per-line dock trips, allowed incomparable workloads and omitted new placement/movement plans. The new workflow addresses these with hard feasibility checks, pairwise packaging proxy, assignment route estimates, identical workload evaluation and staged plans. Original generic random/PRIME helpers remain illustrative legacy APIs, not valid grocery recommendations. No meters and productivity share a chart axis.


## Incoming-case ranking update

Incoming options now rank by eight-nearest-neighbor case compatibility, change in existing historical sequence proxy, frequency access preference and relocation penalty. See the README for the exact formula and assumptions. `score_components` exposes each term; `search_truncated` reports exhaustion of the location-check budget. Stability summaries now use declared location route order when locations are supplied.
