# Roadmap

## v0.1.x Stabilization
- Improve parameter validation and error messages.
- Add deterministic snapshot tests for simulation output ranges.
- Add export package containing all run artifacts in one zip.

## v0.2.0 Data Integration
- Add "real data mode" with CSV ingestion:
  - SKU master
  - Order history
  - Current slot assignments
  - Truck/ASN history
- Add schema validation and data quality checks.
- Compare synthetic vs real-data runs in dashboard.

## v0.3.0 Optimization Upgrade
- Introduce constrained optimization (OR-Tools/Pyomo):
  - Move limits per shift
  - Hazard/weight compatibility
  - Zone constraints
- Add net-benefit model:
  - travel saved
  - re-slot labor cost
  - disruption cost

## v0.4.0 Productionization
- Add FastAPI service for simulation/slotting APIs.
- Add audit logging and versioned recommendation records.
- Add authentication and role-based approval workflow.
- Deploy with CI/CD and observability dashboard.
