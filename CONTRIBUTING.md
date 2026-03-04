# Contributing

## Setup
1. Use Python 3.11.
2. Create a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Local Validation
Run tests before pushing:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

Run app:
```bash
streamlit run app/streamlit_app.py
```

## Branch and PR Rules
- Branch from `main` with clear branch names:
  - `feature/...`
  - `fix/...`
  - `docs/...`
- Keep PRs focused and small.
- Include impact summary for simulation behavior/KPIs.

## Code Guidelines
- Keep logic modular in `src/`.
- Add tests for behavior changes.
- Keep random-seed-driven reproducibility for simulation paths.
- Update README and CHANGELOG when user-visible behavior changes.
