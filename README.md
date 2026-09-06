# Algo-TF

Dynamic, audit-friendly decision architecture for agentic trading research.

## Run locally

```bash
python3 -m algof.server
```

Open `http://localhost:8000`. The included screen and dataset are clearly labeled synthetic fixtures. The server does not contain a broker adapter and cannot place orders.

## Architecture

- Research observations are timestamped, cutoff-filtered evidence, not mandatory gates.
- Read-only advisers receive bounded, one-pass information requests. Their errors and timeouts are recorded without blocking the cycle.
- Empirical probabilities use resolved historical outcomes available at the decision cutoff and report provenance and Wilson intervals.
- Account authorization, permitted actions, cash, position limits, and truthful pricing remain execution constraints.
- Human reviews bind to the decision ID and immutable dataset snapshot ID. Expired or mismatched reviews are rejected.

Run the focused synthetic checks with:

```bash
python3 -m unittest tests/test_engine.py -v
```

Synthetic fixtures test architecture behavior only; they do not demonstrate trading profitability.
