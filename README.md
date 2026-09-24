# FastBox Mystery Delivery System

[![CI](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml/badge.svg)](https://github.com/VarunKumar123456/fastbox-delivery-system/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Type checked](https://img.shields.io/badge/type--checked-mypy-informational)](https://mypy.readthedocs.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A deterministic Python implementation of the **FastBox Mystery Delivery System**, built as a submission for the Nexgensis Software Engineer Intern assignment.

The system reads warehouses, delivery agents, and packages from JSON, assigns packages to agents using capacity constraints, simulates delivery routes using Euclidean distance, and produces a structured performance report.

It also includes a lightweight Flask web interface for running the simulation through a browser.

---

## Live Demo

**Recruiter-facing web demo:**

https://fastbox-delivery-system-dit7.onrender.com

The live demo allows you to:

* Run the delivery simulation from a browser
* Upload a custom JSON input file
* View the best-performing agent
* View packages delivered by each agent
* View total route distance
* View delivery efficiency

The web layer is intentionally lightweight; the core Python simulation remains the source of truth for the assignment logic.

---

## Repository

GitHub:

https://github.com/VarunKumar123456/fastbox-delivery-system

---

## Why This Project

The implementation focuses on the core engineering requirements of the assignment:

* Correct JSON input handling
* Package-to-agent assignment with capacity constraints
* Warehouse and destination routing
* Euclidean distance calculation
* Delivery simulation
* Agent performance metrics
* Deterministic execution
* Input validation and clear errors
* Automated testing
* Static type checking
* Continuous integration
* Docker support
* Optional bonus functionality
* Browser-based demonstration

The implementation is structured into small modules so that the business logic is independent of the CLI and web interfaces.

---

## Requirement Checklist

| Requirement                    | Status   |
| ------------------------------ | -------- |
| Load JSON input                | Complete |
| Validate input data            | Complete |
| Assign packages to agents      | Complete |
| Respect agent capacity         | Complete |
| Simulate delivery routes       | Complete |
| Calculate Euclidean distance   | Complete |
| Calculate agent metrics        | Complete |
| Identify best-performing agent | Complete |
| Generate JSON report           | Complete |
| Deterministic execution        | Complete |
| Automated tests                | Complete |
| Type checking with mypy        | Complete |
| CI with GitHub Actions         | Complete |
| Docker support                 | Complete |
| ASCII route map bonus          | Complete |
| Random delivery delay bonus    | Complete |
| Top performer CSV export bonus | Complete |
| Browser-based web demo         | Complete |

---

## Architecture

```text
FastBox Mystery Delivery System
│
├── src/
│   ├── assignment.py
│   ├── bonus.py
│   ├── data_loader.py
│   ├── models.py
│   ├── simulation.py
│   └── main.py
│
├── web/
│   ├── app.py
│   └── templates/
│       └── index.html
│
├── tests/
│   ├── test_assignment.py
│   ├── test_data_loader.py
│   ├── test_main.py
│   ├── test_simulation.py
│   └── ...
│
├── sample_data/
├── data.json
├── report.json
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Core responsibilities

**`data_loader.py`**

Loads and validates the JSON input.

**`models.py`**

Contains the main domain data structures for warehouses, agents, and packages.

**`assignment.py`**

Handles package assignment while respecting agent capacity.

**`simulation.py`**

Simulates delivery routes and calculates performance metrics.

**`bonus.py`**

Contains optional features such as ASCII map rendering and CSV export.

**`main.py`**

Provides the command-line interface and coordinates the complete workflow.

**`web/app.py`**

Provides the browser-based interface using Flask.

---

## Input Handling

The application accepts JSON input containing:

* Warehouses
* Delivery agents
* Packages

Example structure:

```json
{
  "warehouses": [
    {
      "id": "W1",
      "location": [0, 0]
    }
  ],
  "agents": [
    {
      "id": "A1",
      "location": [0, 0],
      "capacity": 5
    }
  ],
  "packages": [
    {
      "id": "P1",
      "warehouse_id": "W1",
      "destination": [3, 4]
    }
  ]
}
```

The loader validates required fields and rejects malformed or inconsistent input with clear errors.

---

## Assignment Algorithm

Packages are assigned to available agents while respecting each agent's capacity.

The assignment process ensures that:

* Every package is assigned exactly once.
* An agent cannot exceed its configured capacity.
* Invalid warehouse references are rejected.
* Assignment remains deterministic for the same input.

The implementation keeps the assignment logic separate from route simulation so that each stage can be tested independently.

---

## Route Simulation

For each assigned package, the simulation calculates the delivery route using Euclidean distance.

The route consists of:

```text
Agent → Warehouse → Destination
```

For a coordinate pair `(x1, y1)` and `(x2, y2)`, the distance is:

```text
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

The total distance for an agent is the sum of the distances required to complete all assigned deliveries.

---

## Performance Metrics

For each delivery agent, the generated report contains:

```json
{
  "packages_delivered": 2,
  "total_distance": 121.21,
  "efficiency": 60.61
}
```

Efficiency is calculated from the agent's delivery performance and route distance according to the assignment requirements.

The report also identifies the best-performing agent based on the calculated efficiency metric.

---

## Example Report

Running the bundled `data.json` produces:

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

The exact output is deterministic for the same input and configuration.

---

## Deterministic Behavior

The core simulator does not rely on uncontrolled randomness.

The optional delay simulation supports an explicit random seed:

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --delays \
  --seed 42
```

Providing the same input and seed produces reproducible results.

---

## Integrity Check

The CLI performs a final consistency check before writing the report.

The number of reported delivered packages must equal the number of packages in the input.

If the counts do not match, execution fails with a clear error rather than silently producing an incorrect report.

---

## Testing

The project uses `pytest` for automated testing.

Run:

```bash
python -m pytest tests/ -v
```

Current local test result:

```text
12 collected
11 passed
1 skipped
0 failed
```

The skipped test corresponds to the private official assignment fixtures, which are not included in this repository.

No private test cases were fabricated or added to make the test suite appear complete.

---

## Type Checking

The project uses `mypy` for static type checking.

Run:

```bash
python -m mypy src/ --ignore-missing-imports
```

Current result:

```text
Success: no issues found in 9 source files
```

---

## Continuous Integration

GitHub Actions automatically runs the project's checks when changes are pushed.

The CI workflow verifies the code using the project's automated test and quality checks.

GitHub Actions:

https://github.com/VarunKumar123456/fastbox-delivery-system/actions

---

## Optional Features

The project includes several additional features beyond the core requirements.

### ASCII Route Map

Run:

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --ascii-map
```

This prints a simple text-based representation of the delivery environment.

### Random Delivery Delays

Run:

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --delays \
  --seed 42
```

The seed makes the simulation reproducible.

### Top Performer CSV Export

Run:

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --export-top top_performer.csv
```

This exports the selected top performer's statistics to a CSV file.

---

## CLI Usage

### Standard execution

```bash
python -m src.main --input data.json --output report.json
```

### ASCII map

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --ascii-map
```

### Delivery delays

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --delays \
  --seed 42
```

### CSV export

```bash
python -m src.main \
  --input data.json \
  --output report.json \
  --export-top top_performer.csv
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

---

## Web Demo

The project includes a small Flask application under `web/`.

```text
web/
├── app.py
└── templates/
    └── index.html
```

The web application provides:

1. A simple recruiter-facing interface.
2. Optional JSON file upload.
3. Simulation execution.
4. Best-agent display.
5. Agent performance table.
6. Error handling for invalid input.

### Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the web application:

```bash
python -m web.app
```

Then open:

```text
http://127.0.0.1:5000
```

For production deployment, the included Docker configuration starts the application with Gunicorn.

---

## Docker

The project includes a Dockerfile for running the web application.

Build the image:

```bash
docker build -t fastbox-delivery-system .
```

Run the web application:

```bash
docker run --rm -p 10000:10000 fastbox-delivery-system
```

Then open:

```text
http://localhost:10000
```

### Running the CLI inside Docker

The default Docker command starts the web application.

To run the CLI explicitly:

```bash
docker run --rm fastbox-delivery-system \
  python -m src.main \
  --input data.json \
  --output report.json
```

---

## Installation

### Requirements

* Python 3.9+
* Git
* Optional: Docker

Clone the repository:

```bash
git clone https://github.com/VarunKumar123456/fastbox-delivery-system.git
cd fastbox-delivery-system
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the simulator:

```bash
python -m src.main --input data.json --output report.json
```

---

## Engineering Decisions & Assumptions

### Standard library for core logic

The main simulation logic uses Python's standard library wherever practical.

This keeps the core implementation lightweight and easy to execute.

### Separate domain logic from interfaces

The simulation logic is independent of both the CLI and Flask web layer.

This allows the same core implementation to be used by:

* CLI execution
* Automated tests
* Browser demo
* Docker deployment

### Explicit validation

Invalid input is rejected early instead of allowing malformed data to propagate through the simulation.

### Deterministic execution

The core algorithm is deterministic.

Random behavior exists only in the optional delay simulation and can be controlled using a seed.

### Clear failure behavior

The CLI exits with a non-zero status when invalid input or an integrity error is encountered.

This makes the application suitable for automated scripts and CI environments.

---

## Code Quality

The project emphasizes:

* Type hints
* Small focused modules
* Explicit validation
* Reusable functions
* Deterministic behavior
* Automated tests
* Static type checking
* CI verification
* Clear CLI error handling
* Separation of business logic and presentation

The implementation is designed to remain understandable while keeping the assignment logic straightforward.

---

## Project Complexity

Let:

* `P` = number of packages
* `A` = number of delivery agents

The package assignment process is designed around the available agent capacity and package allocation requirements.

Route simulation processes each assigned package and calculates the required coordinate distances.

The overall implementation is intentionally simple enough for the assignment scale while keeping the main operations separated for testing and maintenance.

---

## Submission Notes

The repository contains:

* Complete source code
* Automated tests
* Type checking configuration
* GitHub Actions CI
* Docker configuration
* Sample input
* Generated report
* Flask web demo
* Documentation

The live web demo is deployed separately from the core simulation and provides a convenient way to verify the application behavior through a browser.

---

## Self-Review

The implementation was reviewed against the assignment requirements with emphasis on:

* Correct input parsing
* Capacity-aware assignment
* Route calculation
* Delivery metrics
* Report generation
* Deterministic behavior
* Error handling
* Automated testing
* Type checking
* CI
* Docker execution
* Browser-based demonstration

The repository intentionally does not include private official assignment fixtures that were not provided as part of the public project files.

---

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
