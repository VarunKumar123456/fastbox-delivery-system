"""
Agent-package assignment.

Rule from the brief: "Assign each package to the nearest agent based
on Euclidean distance from agent to warehouse."

Documented assumptions (per the client's instruction to make and note
reasonable calls instead of pausing for clarification):

1. "Distance from agent to warehouse" is measured from each agent's
   starting location for the day (not a location that updates mid-run
   as the agent gets busy). This matches the wording literally and
   keeps assignment a clean, independent step before simulation.
2. Tie-break: if two or more agents are exactly equidistant from a
   package's warehouse, the agent with the lexicographically smallest
   ID is chosen, for deterministic, reproducible output.
3. Bonus - "handle new agent joining mid-day": an Agent may carry a
   `joined_at` package index (0 = available all day). An agent is only
   considered for packages processed at or after that index. This is
   opt-in and has no effect unless the caller sets joined_at on an
   agent, so it never changes behavior for the base test cases.
"""

from typing import Dict, List

from .distance import euclidean
from .models import Agent, Package, Warehouse


def assign_packages(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package],
) -> List[Package]:
    if not agents:
        raise ValueError("Cannot assign packages: no agents available.")

    for index, package in enumerate(packages):
        warehouse = warehouses[package.warehouse_id]

        eligible_agents = [a for a in agents.values() if a.joined_at <= index] or list(agents.values())

        best_agent = min(
            eligible_agents,
            key=lambda a: (euclidean(a.location, warehouse.location), a.id),
        )
        package.assigned_agent = best_agent.id

    return packages
