"""
Optional bonus features (all opt-in via CLI flags in main.py, none are
required for a passing core simulation):

  - ASCII visualization of warehouses / agents / package destinations
  - CSV export of the top-performing agent
  - "new agent joining mid-day" is implemented in assignment.py via
    Agent.joined_at, since it belongs to the assignment step itself.
"""

import csv
from typing import Dict, List, Optional

from .models import Agent, AgentReport, Package, Warehouse


def render_ascii_map(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package],
    width: int = 60,
    height: int = 25,
) -> str:
    """Plots warehouses (W), agent start points (A), and package
    destinations (.) onto a simple text grid, scaled to fit."""
    all_points = (
        [w.location for w in warehouses.values()]
        + [a.location for a in agents.values()]
        + [p.destination for p in packages]
    )
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x) or 1
    span_y = (max_y - min_y) or 1

    grid = [[" "] * width for _ in range(height)]

    def plot(x: float, y: float, ch: str) -> None:
        col = int((x - min_x) / span_x * (width - 1))
        row = int((y - min_y) / span_y * (height - 1))
        row = height - 1 - row  # flip so +y is "up"
        grid[row][col] = ch

    for p in packages:
        plot(p.destination[0], p.destination[1], ".")
    for w in warehouses.values():
        plot(w.location[0], w.location[1], "W")
    for a in agents.values():
        plot(a.location[0], a.location[1], "A")

    lines = ["".join(row) for row in grid]
    legend = "Legend: W = warehouse, A = agent start, . = package destination"
    return "\n".join(lines) + "\n" + legend


def export_top_performer_csv(
    reports: Dict[str, AgentReport], best_agent: str, path: str
) -> None:
    """Writes the top-performing agent's stats (and delivered package
    IDs) to a single-row CSV file."""
    report = reports[best_agent]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["agent_id", "packages_delivered", "total_distance", "efficiency", "delivered_package_ids"]
        )
        writer.writerow(
            [
                report.agent_id,
                report.packages_delivered,
                round(report.total_distance, 2),
                round(report.efficiency, 2),
                ";".join(report.delivered_package_ids),
            ]
        )
