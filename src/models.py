"""
Core data models for the FastBox delivery simulation.

Using lightweight dataclasses keeps the domain objects self-documenting
and avoids passing raw dicts/tuples around the rest of the codebase.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Coordinate = Tuple[float, float]


@dataclass(frozen=True)
class Warehouse:
    id: str
    location: Coordinate


@dataclass
class Agent:
    id: str
    location: Coordinate          # starting location for the day
    joined_at: int = 0            # bonus: package index at which agent becomes available (0 = start of day)


@dataclass
class Package:
    id: str
    warehouse_id: str
    destination: Coordinate
    assigned_agent: Optional[str] = None  # filled in by the assignment stage
    delay: float = 0.0            # bonus: simulated random delay (minutes), does not affect distance


@dataclass
class AgentReport:
    agent_id: str
    packages_delivered: int = 0
    total_distance: float = 0.0
    efficiency: float = 0.0       # average distance travelled per package delivered (lower = better)
    delivered_package_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "packages_delivered": self.packages_delivered,
            "total_distance": round(self.total_distance, 2),
            "efficiency": round(self.efficiency, 2),
        }
