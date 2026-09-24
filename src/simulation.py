"""
Simulates one day of deliveries and builds the final report.

Rule from the brief: "agent picks up packages from warehouse and
delivers to destination. Compute total distance traveled."

Documented assumptions:

1. Each agent may be assigned more than one package. Its route for the
   day is built by visiting its assigned packages in the same order
   they appear in the input `packages` list (a stable, reproducible
   ordering), travelling: current_position -> warehouse -> destination,
   and the destination becomes the agent's new current_position for
   the next package. This models a realistic single continuous route
   rather than the agent teleporting back to its start between drops.
2. "efficiency" is computed as total_distance / packages_delivered
   (average distance travelled per package). This is verified against
   the worked example in the brief: A1 -> 85.32 / 2 = 42.66,
   A2 -> 120.12 / 2 = 60.06, A3 -> 50.00 / 1 = 50.00, which matches
   exactly. Because this metric is a *cost* (lower = better), the most
   efficient agent is the one with the MINIMUM value -- also confirmed
   by the example, where A1 has both the lowest efficiency and is
   `best_agent`.
3. An agent assigned zero packages still appears in the report with
   packages_delivered=0, total_distance=0.0, efficiency=0.0, and is
   never selected as best_agent (an idle agent didn't out-perform
   anyone).
4. Bonus - random delivery delays: delays are simulated in minutes and
   reported separately per package; they represent time, not distance,
   so they never affect total_distance/efficiency.
"""

import random
from typing import Dict, List, Optional, Tuple

from .distance import euclidean
from .models import Agent, AgentReport, Package, Warehouse


def simulate_deliveries(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package],
    apply_random_delays: bool = False,
    random_seed: Optional[int] = None,
) -> Tuple[Dict[str, AgentReport], Optional[str]]:
    if random_seed is not None:
        random.seed(random_seed)

    reports: Dict[str, AgentReport] = {
        agent_id: AgentReport(agent_id=agent_id) for agent_id in agents
    }
    current_position: Dict[str, Tuple[float, float]] = {
        agent_id: agent.location for agent_id, agent in agents.items()
    }

    for package in packages:
        agent_id = package.assigned_agent
        if agent_id is None:
            raise ValueError(f"Package {package.id} has not been assigned to an agent yet.")

        warehouse = warehouses[package.warehouse_id]
        report = reports[agent_id]

        leg_to_warehouse = euclidean(current_position[agent_id], warehouse.location)
        leg_to_destination = euclidean(warehouse.location, package.destination)

        report.total_distance += leg_to_warehouse + leg_to_destination
        report.packages_delivered += 1
        report.delivered_package_ids.append(package.id)
        current_position[agent_id] = package.destination

        if apply_random_delays:
            package.delay = round(random.uniform(0, 30), 1)  # minutes

    for report in reports.values():
        report.efficiency = (
            report.total_distance / report.packages_delivered
            if report.packages_delivered > 0
            else 0.0
        )

    active_reports = [r for r in reports.values() if r.packages_delivered > 0]
    best_agent = min(active_reports, key=lambda r: r.efficiency).agent_id if active_reports else None

    return reports, best_agent


def build_report(reports: Dict[str, AgentReport], best_agent: Optional[str]) -> Dict[str, object]:
    output: Dict[str, object] = {agent_id: report.to_dict() for agent_id, report in reports.items()}
    output["best_agent"] = best_agent
    return output
