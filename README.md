# FastBox Mystery Delivery System

[![CI](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml/badge.svg)](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Type checked](https://img.shields.io/badge/type--checked-mypy-informational)](https://mypy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A modular Python simulator for one day of FastBox logistics.

The system reads delivery data, assigns each package to the nearest eligible agent, simulates the resulting delivery routes, calculates per-agent performance metrics, and produces a deterministic JSON report.

The implementation focuses on **correctness, clear separation of responsibilities, deterministic behavior, input validation, testability, and maintainability**.

---

## Why This Project

The core problem is simple:

> Given warehouses, delivery agents, and packages, determine which agent should handle each package and simulate the resulting deliveries.

The implementation separates the problem into independent stages:

**Load → Validate → Assign → Simulate → Report**

This makes the system easier to test, reason about, and extend without coupling unrelated parts of the application.

---

## Requirement Checklist

| Requirement                        | Status | Implementation          |
| ---------------------------------- | :----: | ----------------------- |
| Read and parse `data.json`         |    ✅   | `src/data_loader.py`    |
| Assign packages to nearest agent   |    ✅   | `src/assignment.py`     |
| Use Euclidean distance             |    ✅   | `src/distance.py`       |
| Simulate package deliveries        |    ✅   | `src/simulation.py`     |
| Calculate total distance           |    ✅   | `src/simulation.py`     |
| Calculate delivery efficiency      |    ✅   | `src/simulation.py`     |
| Generate required report structure |    ✅   | `build_report()`        |
| Write `report.json`                |    ✅   | `src/main.py`           |
| Validate malformed input           |    ✅   | `src/data_loader.py`    |
| Ensure all packages are delivered  |    ✅   | Runtime integrity check |
| Deterministic tie-breaking         |    ✅   | `src/assignment.py`     |
| Type checking                      |    ✅   | `mypy`                  |
| Automated testing                  |    ✅   | `pytest`                |
| Continuous Integration             |    ✅   | GitHub Actions          |
| Dockerized execution               |    ✅   | `Dockerfile`            |

---

## Architecture

```text
fastbox-delivery-system/
│
├── src/
│   ├── models.py
│   │   └── Domain models and typed data structures
│   │
│   ├── data_loader.py
│   │   └── JSON parsing, validation and schema normalization
│   │
│   ├── distance.py
│   │   └── Euclidean distance calculation
│   │
│   ├── assignment.py
│   │   └── Nearest eligible-agent assignment
│   │
│   ├── simulation.py
│   │   └── Route simulation and report generation
│   │
│   ├── bonus.py
│   │   └── Optional ASCII visualization and CSV export
│   │
│   └── main.py
│       └── CLI entry point and application orchestration
│
├── tests/
│   └── test_delivery_system.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── data.json
├── report.json
├── sample_data/
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── LICENSE
└── README.md
```

### Design

The application follows a small, modular pipeline:

```text
             ┌──────────────┐
             │   JSON Input │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ Load &       │
             │ Validate     │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ Assignment   │
             │              │
             │ nearest      │
             │ agent        │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ Simulation   │
             │              │
             │ route +      │
             │ distance     │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │ Report       │
             │              │
             │ JSON output  │
             └──────────────┘
```

Each stage has a focused responsibility, allowing individual components to be tested independently.

---

## Input Handling

The loader supports both input representations encountered in the assignment materials.

### Dictionary-style locations

```json
{
  "warehouses": {
    "W1": [10, 20]
  }
}
```

### List-style locations

```json
{
  "warehouses": [
    {
      "id": "W1",
      "location": [10, 20]
    }
  ]
}
```

The loader normalizes both representations into the same internal model.

Invalid data is rejected with explicit errors rather than failing later with ambiguous exceptions.

Examples of validation include:

* Missing required fields
* Unknown warehouse references
* Unsupported data structures
* Invalid package definitions

---

## Assignment Algorithm

For every package:

1. Identify the package's warehouse.
2. Determine the eligible delivery agents.
3. Calculate Euclidean distance from each eligible agent's starting location to the warehouse.
4. Select the nearest agent.
5. Apply deterministic ID-based tie-breaking when distances are equal.

The distance function is centralized in `src/distance.py`, providing a single source of truth for the geometry calculation.

### Complexity

For:

* `P` = number of packages
* `A` = number of agents

Assignment complexity is:

```text
O(P × A)
```

This is a straightforward linear search over eligible agents for each package and is appropriate for the scale of the assignment.

For substantially larger agent populations, the assignment layer could be replaced with a spatial index such as a k-d tree without changing the rest of the pipeline.

---

## Route Simulation

Once packages are assigned, each agent's route is simulated sequentially.

For an agent handling multiple packages:

```text
Current Position
      ↓
Warehouse
      ↓
Destination
      ↓
Next Package
      ↓
Warehouse
      ↓
Destination
```

The destination of one delivery becomes the starting position for the next delivery.

This produces a continuous route rather than resetting an agent to its original location after every package.

---

## Performance Metrics

For every agent, the generated report contains:

```json
{
  "packages_delivered": 2,
  "total_distance": 121.21,
  "efficiency": 60.61
}
```

The efficiency metric used by the implementation is:

```text
efficiency = total_distance / packages_delivered
```

This represents average distance travelled per delivered package.

Agents with zero assigned packages remain represented in the report with zero-valued metrics and are excluded from selection as the best performing agent.

---

## Deterministic Behavior

Determinism is important for reproducible tests and debugging.

When two agents are exactly the same distance from a warehouse, the agent with the lexicographically smaller ID is selected.

This ensures that identical input produces consistent assignment results.

---

## Report

Running the application against the supplied `data.json` produces:

```json
{
  "A1": {
    "packages_delivered": 2,
    "total_distance": 121.21,
    "efficiency": 60.61
  },
  "A2": {
    "packages_delivered": 2,
    "total_distance": 79.21,
    "efficiency": 39.6
  },
  "A3": {
    "packages_delivered": 1,
    "total_distance": 14.14,
    "efficiency": 14.14
  },
  "best_agent": "A3"
}
```

The application also performs a runtime integrity check to ensure:

```text
packages delivered == packages provided
```

If the invariant is violated, execution fails instead of silently producing an inconsistent report.

---

## Testing

The project uses `pytest`.

The current test suite contains **12 collected tests**:

```text
11 passed
1 skipped
0 failed
```

The skipped test checks the separate official assignment fixture set. Those private fixture files are not included in this repository, so the test intentionally skips when that fixture directory is unavailable.

The implemented tests cover:

* Euclidean distance calculation
* Dictionary-style input
* List-style input
* Invalid warehouse references
* Missing required fields
* Nearest-agent assignment
* Deterministic tie-breaking
* Full delivery simulation
* Efficiency calculation
* Zero-package agents
* Report structure
* Official fixture validation when the supplied fixtures are available

### Verified locally

```text
pytest
12 collected
11 passed
1 skipped
0 failed
```

### Static type checking

```text
Success: no issues found in 8 source files
```

---

## Continuous Integration

GitHub Actions runs the project's automated checks on pushes and pull requests.

The CI pipeline validates the project using:

```text
mypy
pytest
application simulation
```

Current CI status:

[![CI](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml/badge.svg)](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml)

---

## Optional Features

Several features are implemented as opt-in extensions so they do not change the default assignment behavior.

### Random delivery delays

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --delays \
  --seed 42
```

A seed can be supplied to make the randomized delay simulation reproducible.

The delay affects simulated time only and does not change the distance calculation.

### ASCII route visualization

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --ascii-map
```

This provides a lightweight terminal visualization of warehouses, agents, and destinations.

### CSV top-performer export

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --export-top top_performer.csv
```

### Agents joining during the day

The `Agent` model supports a `joined_at` value indicating the package-list position from which an agent becomes eligible for assignment.

Example:

```python
Agent(
    id="A4",
    location=(50, 50),
    joined_at=6,
)
```

This allows an agent to become available during the simulation without changing the default behavior of existing agents.

---

## CLI Usage

### Standard execution

```bash
python -m src.main \
  --input data.json \
  --output report.json
```

### All optional features

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --ascii-map \
  --delays \
  --seed 42 \
  --export-top top_performer.csv
```

### CLI options

| Option              | Description                              |
| ------------------- | ---------------------------------------- |
| `--input PATH`      | Input JSON file                          |
| `--output PATH`     | Output report JSON                       |
| `--ascii-map`       | Display route information as ASCII       |
| `--delays`          | Add simulated 0–30 minute package delays |
| `--seed N`          | Seed randomized delay generation         |
| `--export-top PATH` | Export top-performer information to CSV  |

---

## Docker

The application can also be executed in a container.

### Build

```bash
docker build -t fastbox-delivery .
```

### Run

```bash
docker run --rm -v "$(pwd)":/app/out fastbox-delivery
```

The containerized execution provides a reproducible environment without requiring the project's Python dependencies to be installed locally.

---

## Installation

### Requirements

* Python 3.9+
* Docker (optional)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run tests

```bash
python -m pytest tests/ -v
```

### Run type checking

```bash
python -m mypy src/ --ignore-missing-imports
```

### Run application

```bash
python -m src.main --input data.json --output report.json
```

---

## Engineering Decisions & Assumptions

### 1. Agent starting position

Assignment distance is measured from an agent's starting location to the package warehouse.

The assignment stage is intentionally independent of the later route simulation.

### 2. Tie-breaking

Equal-distance assignments are resolved using the lexicographically smallest agent ID.

This keeps the output deterministic.

### 3. Multiple packages

Packages assigned to the same agent are simulated sequentially.

The destination of one delivery becomes the agent's current position for the next delivery.

### 4. Efficiency

```text
total_distance / packages_delivered
```

This measures average distance per delivered package.

### 5. Idle agents

Agents with no assigned packages remain in the report but are not selected as the best agent.

### 6. Input normalization

The loader accepts the different warehouse/agent representations encountered in the supplied assignment data and converts them into one internal representation.

---

## Code Quality

The project emphasizes:

* Type hints throughout the core code
* Small focused modules
* Dataclasses for domain models
* Explicit validation
* Deterministic behavior
* Unit/integration tests
* Runtime invariants
* CI automation
* Docker support
* Minimal external dependencies
* Clear separation between core functionality and optional features

The core application uses Python's standard library for runtime functionality.

---

## Project Complexity

| Stage      | Complexity     |
| ---------- | -------------- |
| Parsing    | `O(W + A + P)` |
| Assignment | `O(P × A)`     |
| Simulation | `O(P)`         |
| Overall    | `O(P × A)`     |

Where:

* `W` = warehouses
* `A` = agents
* `P` = packages

The assignment stage dominates runtime because each package performs a nearest-agent search.

For very large datasets, the assignment strategy could be optimized using a spatial indexing structure such as a k-d tree.

---

## Live Demo

A browser-based demonstration of the same assignment and simulation concepts is available here:

https://claude.ai/artifact/4bSvYfMdf5BSC8Zsps1oey

The production implementation in this repository remains the source of truth for the Python solution.

---

## Repository

GitHub:

https://github.com/VarunKumar123456/fastbox-delivery-system

---

## Self-Review

The implementation addresses the main assignment requirements with:

* Manual JSON parsing and normalization
* Euclidean distance calculation
* Nearest-agent assignment
* Deterministic tie-breaking
* Route simulation
* Required report generation
* Package-count integrity validation
* Input validation
* Automated tests
* Static type checking
* GitHub Actions CI
* Docker support

Optional extensions include:

* Randomized delivery delays
* Reproducible delay simulation
* ASCII route visualization
* Mid-day agent joining
* CSV export

The implementation deliberately keeps these extensions opt-in so the core assignment behavior remains simple and predictable.

---

## License

MIT License.

See [LICENSE](LICENSE) for details.
