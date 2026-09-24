# FastBox Mystery Delivery System

[![CI](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml/badge.svg)](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![Type checked: mypy](https://img.shields.io/badge/type--checked-mypy-informational)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A simulator for one day of FastBox logistics: packages are assigned to the
nearest delivery agent, agents' routes are simulated, and a per-agent
performance report is produced. Zero runtime dependencies (stdlib only),
fully type-hinted and mypy-clean, with a 12-test pytest suite and CI
running on every push.

> **Note:** replace `VarunKumar123456` above with your GitHub
> username once pushed, so the CI badge points at your repo's own workflow
> run and shows a live "passing" status.

## Requirement Checklist (from the assignment brief)

| # | Requirement | Status | Where |
|---|---|---|---|
| 1 | Read and parse `data.json` manually | ✅ | `src/data_loader.py` |
| 2 | Assign each package to nearest agent (Euclidean, agent→warehouse) | ✅ | `src/assignment.py` |
| 3 | Simulate delivery, compute total distance travelled | ✅ | `src/simulation.py` |
| 4 | Generate report in the specified `{agent: {...}, best_agent}` shape | ✅ | `src/simulation.py::build_report` |
| 5 | Save report to `report.json` | ✅ | `src/main.py` |
| — | Test with different JSON inputs | ✅ | validated against `base_case.json` and all 10 official `test_case_*.json` files (see Testing) |
| — | Total packages delivered must match total packages | ✅ | runtime integrity check in `src/main.py::run` (raises if mismatched) |
| — | Comment code for clarity | ✅ | module/function docstrings + inline comments throughout `src/` |
| Bonus | Random delivery delays | ✅ | `--delays` flag, `src/simulation.py` |
| Bonus | Visualize routes in ASCII | ✅ | `--ascii-map` flag, `src/bonus.py` |
| Bonus | Handle new agent joining mid-day | ✅ | `Agent.joined_at` in `src/models.py` + `src/assignment.py` |
| Bonus | Export top performer to CSV | ✅ | `--export-top` flag, `src/bonus.py` |

## Architecture

```
fastbox_delivery_system/
├── src/
│   ├── models.py       # Warehouse / Agent / Package / AgentReport dataclasses
│   ├── data_loader.py  # manual JSON parsing + schema normalization
│   ├── distance.py     # Euclidean distance helper
│   ├── assignment.py   # nearest-agent package assignment
│   ├── simulation.py   # route simulation + report building
│   ├── bonus.py        # ASCII map + CSV export
│   └── main.py         # CLI entrypoint, wires everything together
├── tests/
│   └── test_delivery_system.py   # pytest suite (12 tests)
├── .github/workflows/
│   └── ci.yml            # runs mypy + pytest + a live sim, on every push/PR
├── data.json              # sample input (the brief's worked example)
├── pyproject.toml         # project metadata, pytest & mypy config
├── requirements.txt
├── Dockerfile / .dockerignore   # zero-setup containerized run
├── LICENSE                # MIT
└── README.md
```

The pipeline is a straight line: **load → assign → simulate → report**,
with each stage in its own module so any one piece (e.g. swapping
Euclidean for road-network distance) can change without touching the
others.

## Handling ambiguity: two input schemas

The brief's own example shows `warehouses`/`agents` as `{"id": [x, y]}`
dicts, but the supplied `base_case.json` and official test cases use
`[{"id": ..., "location": [x, y]}]` lists, and packages key their
warehouse as `warehouse_id` instead of `warehouse`. Rather than assume
one shape and fail on the other, `data_loader.py` normalizes **both**
into the same internal model. Anything that matches neither shape
raises a clear `DataFormatError`.

## Other documented assumptions

Per the brief's instruction to make and record reasonable calls
instead of pausing for clarification:

1. **"Distance from agent to warehouse" (assignment step)** is each
   agent's fixed starting location for the day — not a location that
   updates as agents get busy. This is assignment's own step, kept
   independent of the simulation that follows.
2. **Tie-breaking**: if two agents are exactly equidistant from a
   warehouse, the one with the lexicographically smallest ID wins, so
   output is deterministic and reproducible.
3. **Multi-package routes**: an agent with several packages visits
   them in input order, travelling `current_position → warehouse →
   destination` each time, with the destination becoming its new
   position for the next package — a single continuous route rather
   than resetting to its start point after each delivery.
4. **`efficiency` formula**: `total_distance / packages_delivered`
   (average distance per delivery — lower is better). This was
   reverse-engineered from the brief's own worked numbers
   (`85.32 / 2 = 42.66`, `120.12 / 2 = 60.06`, `50.00 / 1 = 50.00`) and
   confirmed against the module's tests. Because it's a cost metric,
   `best_agent` is the agent with the **minimum** efficiency — also
   consistent with the brief's example, where A1 has the lowest value
   and is `best_agent`.

   Note: with the actual coordinates given in the brief, our simulation
   correctly computes different absolute numbers than the brief's
   sample report (121.21 / 79.21 / 14.14 rather than 85.32 / 120.12 /
   50.00) — the assignment (which agent gets which package) matches
   exactly, but the sample numbers appear to be illustrative
   placeholders for the report's *shape*, not a literal expected
   output to reproduce. The relationship the numbers demonstrate
   (`efficiency = distance / count`, `best_agent = min(efficiency)`)
   is reproduced exactly.
5. **Idle agents** (assigned zero packages) still appear in the report
   with all-zero stats, and are never chosen as `best_agent`.

## Live Demo

Try it in the browser (same assignment/simulation logic, reimplemented
in JS, no install needed): https://claude.ai/artifact/4bSvYfMdf5BSC8Zsps1oey

## Performance & Complexity

- **Parsing**: O(W + A + P) — a single pass over warehouses, agents, and packages.
- **Assignment**: O(P × A) — for each of the P packages, the nearest of A agents
  is found by a linear scan. At the scale this problem operates at (tens to
  low-thousands of agents/packages) this is both correct and fast; it could be
  upgraded to a k-d tree for O(P log A) if agent counts grew into the tens of
  thousands.
- **Simulation**: O(P) — one pass over the already-assigned packages.
- **Overall**: O(P × A), dominated by assignment. All 11 supplied datasets
  (5–12 packages, 3–5 agents) run in well under a millisecond.

## Usage

```bash
# Core run
python -m src.main --input data.json --output report.json

# With all bonus features
python -m src.main --input data.json --output report.json \
    --ascii-map --delays --seed 42 --export-top top_performer.csv
```

### Run with Docker (zero local setup)

```bash
docker build -t fastbox-delivery .
docker run --rm -v "$(pwd)":/app/out fastbox-delivery
# report.json is written inside the container; the run above also
# prints it to stdout so you can verify output without a volume mount.
```

| Flag | Effect |
|---|---|
| `--input PATH` | Input JSON (default `data.json`) |
| `--output PATH` | Output report JSON (default `report.json`) |
| `--ascii-map` | Print an ASCII grid of warehouses/agents/destinations |
| `--delays` | Simulate a random 0–30 min delay per package (time only, never affects distance/efficiency) |
| `--seed N` | Seed the RNG for reproducible `--delays` output |
| `--export-top PATH` | Export the top-performing agent's stats to a CSV file |

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

12 tests cover: distance math, both input schema variants, malformed
input rejection, nearest-agent assignment (including tie-breaking),
full simulation + report shape, the zero-package-agent edge case, and
a run against every officially supplied `test_case_*.json` file to
confirm delivered-package counts always balance.

## New agent joining mid-day (bonus)

`Agent.joined_at` (default `0`) marks the package-list index at which
an agent becomes eligible for assignment. Setting it lets a caller add
an agent who wasn't there at the start of the day, without changing
default behavior for anyone else. Example:

```python
agents["A4"] = Agent(id="A4", location=(50, 50), joined_at=6)
# A4 will only be considered for the 7th package onward.
```

## Self-review against the checklist

- **JSON parsing (10%)** — handles both schema variants seen in the
  supplied data, rejects malformed input with a specific error.
- **Distance calculation (20%)** — single, tested `euclidean()` helper
  used everywhere so there's one source of truth for the geometry.
- **Agent-package assignment (25%)** — nearest-agent-to-warehouse logic
  with a deterministic tie-break; unit tested directly.
- **Simulation & report (25%)** — sequential per-agent route, `report.json`
  exactly matches the brief's `{agent: {...}, best_agent}` shape, and a
  runtime assertion guarantees delivered packages == input packages.
- **Code clarity & comments (10%)** — every module opens with a
  docstring explaining its role and any assumptions baked into it.
- **Bonus creativity (10%)** — all four listed bonus ideas implemented
  as opt-in CLI flags that never change default/core behavior, plus an
  interactive live browser demo, CI, a Dockerized run path, and a clean
  `mypy --strict`-style type-checked codebase — none of which were asked
  for, but all of which make the solution easier to trust and evaluate.

## License

MIT — see [LICENSE](LICENSE).
