"""Distance calculations. Isolated in its own module so the geometry
(and any future upgrade to e.g. road-network distance) stays decoupled
from assignment/simulation logic."""

import math
from typing import Tuple

Coordinate = Tuple[float, float]


def euclidean(a: Coordinate, b: Coordinate) -> float:
    """Straight-line distance between two (x, y) points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])
