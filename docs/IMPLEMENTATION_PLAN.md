# Implementation Plan

## Objective
Evolve the current digital twin prototype into a production-grade slotting decision platform for grocery warehouse operations.

## Delivery Phases

## Phase 1: Foundation Hardening (2-3 weeks)
### Epic 1: Data Contracts and Validation
1. Define canonical schemas for SKU master, orders, slots, trucks.
Acceptance criteria:
- JSON/CSV schema specs documented.
- Validation errors are explicit and actionable.

2. Build ingestion validators in `src/` for all input datasets.
Acceptance criteria:
- Invalid rows are reported with field-level reason.
- App can run in strict mode (fail on bad data) and permissive mode (drop bad rows).

### Epic 2: Simulation Reliability
3. Add parameter validation layer (ranges, null checks, capacity checks).
Acceptance criteria:
- App rejects invalid configs with clear messages.

4. Add deterministic scenario regression tests with seeded expected ranges.
Acceptance criteria:
- CI fails when simulation output drifts unexpectedly.

5. Add consolidated run artifact export (`zip` with metrics + CSV outputs + config).
Acceptance criteria:
- One-click export from Streamlit produces complete reproducible package.

## Phase 2: Real Data Mode (3-4 weeks)
### Epic 3: Real Data Ingestion
6. Add "Synthetic vs Real Data" mode toggle in UI.
Acceptance criteria:
- Real mode supports user-uploaded CSV templates.

7. Build template files and parser for:
- `sku_master.csv`
- `order_history.csv`
- `slot_assignments.csv`
- `truck_asn.csv`
Acceptance criteria:
- Templates documented and downloadable from app.

8. Add data quality report page (completeness, uniqueness, type errors).
Acceptance criteria:
- Report shows row counts, rejected rows, and key anomalies.

### Epic 4: Model Calibration
9. Add calibration settings for walking speed, handling time, and shift profile.
Acceptance criteria:
- Parameters saved and reused between runs.

10. Add "Backtest" view comparing simulated vs historical productivity.
Acceptance criteria:
- Shows error metrics (MAE/MAPE) for distance and throughput proxies.

## Phase 3: Optimization Upgrade (4-5 weeks)
### Epic 5: Constrained Optimization Engine
11. Introduce OR-Tools/Pyomo optimizer with constraints:
- max moves/day
- ergonomic rules
- weight/hazard compatibility
- zone restrictions
Acceptance criteria:
- Solver returns feasible slot plan with explainable constraint outcomes.

12. Add policy configuration UI for constraints and objective weights.
Acceptance criteria:
- Users can save/load named policies.

13. Add fallback behavior when no feasible solution exists.
Acceptance criteria:
- App returns nearest-feasible or explains violated constraints.

### Epic 6: Event-Driven Re-slotting
14. Add re-slot triggers:
- new SKU introduction
- velocity class changes
- seasonal uplift
- congestion threshold breaches
Acceptance criteria:
- Trigger events produce targeted re-slot candidate list.

15. Add wave planning screen (who moves what, when, and estimated move hours).
Acceptance criteria:
- Wave includes per-SKU move details and expected gain.

16. Add net-benefit model:
- travel savings
- move labor cost
- disruption penalty
Acceptance criteria:
- Decision gate outputs GO/NO-GO with rationale.

## Phase 4: Productionization (4-6 weeks)
### Epic 7: Service Layer and Governance
17. Build FastAPI service endpoints:
- `/simulate`
- `/optimize`
- `/artifacts/{run_id}`
Acceptance criteria:
- API documented with OpenAPI and versioned contracts.

18. Add run registry and audit trail (inputs, outputs, user, timestamp).
Acceptance criteria:
- Every recommendation is reproducible and queryable.

19. Add role-based workflow:
- analyst proposes
- manager approves
- ops executes
Acceptance criteria:
- Approval state machine enforced.

### Epic 8: DevOps and Observability
20. Add deployment manifests and environment configs.
Acceptance criteria:
- Dev/stage/prod deploy instructions documented.

21. Add monitoring dashboards:
- API latency
- job success/failure
- data freshness
- key business KPIs
Acceptance criteria:
- Alert thresholds defined for operational incidents.

22. Add security baseline:
- secret management
- access controls
- dependency scanning
Acceptance criteria:
- Security checklist passes for release candidate.

## Prioritized Backlog (Top 12)
1. Real data mode toggle + CSV ingestion templates.
2. Input schema validation with strict/permissive mode.
3. Data quality report page.
4. Parameter validation for simulation config.
5. Export all run artifacts as single zip.
6. Calibration settings and persistence.
7. Backtest view (simulated vs historical).
8. OR-Tools/Pyomo constrained optimizer.
9. Constraint policy UI (save/load policy sets).
10. Event-driven re-slot trigger engine.
11. Net-benefit decision gate (GO/NO-GO).
12. FastAPI `/simulate` and `/optimize` service endpoints.

## Suggested GitHub Labels
- `priority:high`
- `priority:medium`
- `priority:low`
- `type:bug`
- `type:feature`
- `type:tech-debt`
- `area:data`
- `area:simulation`
- `area:optimization`
- `area:ui`
- `area:api`
- `area:devops`

## Definition of Done
- Code merged with passing CI.
- Tests added/updated for behavior changes.
- Docs updated (`README`, `CHANGELOG`, plan/roadmap as needed).
- User-visible feature demoed in Streamlit or API endpoint example.
