"""
Manual JSON parsing and normalization.

The assignment brief shows one input shape (warehouses/agents as
id -> [x, y] dicts), but the supplied base_case.json and the ten
official test cases use a second shape (warehouses/agents as lists of
{"id": ..., "location": [...]} objects, and packages keyed by either
"warehouse" or "warehouse_id"). Real-world "mystery" data rarely comes
in one tidy shape, so the loader normalizes both into the same
internal model rather than assuming a single format.

Assumption (documented per the assignment's instruction to make and
record reasonable decisions instead of stopping to ask): any input
that isn't recognizably one of these two shapes raises a clear
DataFormatError rather than silently producing wrong results.
"""

import json
from typing import Any, Dict, List, Tuple

from .models import Agent, Package, Warehouse


class DataFormatError(ValueError):
    """Raised when the input JSON doesn't match a supported schema."""


def _as_coordinate(raw: Any) -> Tuple[float, float]:
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise DataFormatError(f"Expected a [x, y] coordinate, got: {raw!r}")
    x, y = raw
    return float(x), float(y)


def _normalize_located_entities(raw: Any, kind: str) -> Dict[str, Tuple[float, float]]:
    """
    Accepts either:
      {"W1": [0, 0], "W2": [50, 75], ...}                       (dict form)
      [{"id": "W1", "location": [0, 0]}, ...]                   (list form)
    Returns {"W1": (0.0, 0.0), ...}
    """
    result: Dict[str, Tuple[float, float]] = {}

    if isinstance(raw, dict):
        for entity_id, coord in raw.items():
            result[entity_id] = _as_coordinate(coord)
    elif isinstance(raw, list):
        for entry in raw:
            if "id" not in entry or "location" not in entry:
                raise DataFormatError(
                    f"Each {kind} entry must have 'id' and 'location', got: {entry!r}"
                )
            result[entry["id"]] = _as_coordinate(entry["location"])
    else:
        raise DataFormatError(f"'{kind}' must be a dict or a list, got: {type(raw).__name__}")

    if not result:
        raise DataFormatError(f"No {kind} found in input data.")
    return result


def _normalize_packages(raw: Any) -> List[Package]:
    if not isinstance(raw, list):
        raise DataFormatError(f"'packages' must be a list, got: {type(raw).__name__}")

    packages: List[Package] = []
    for entry in raw:
        if "id" not in entry or "destination" not in entry:
            raise DataFormatError(f"Package entry missing 'id' or 'destination': {entry!r}")
        # The brief uses "warehouse"; the supplied base case uses "warehouse_id".
        warehouse_id = entry.get("warehouse") or entry.get("warehouse_id")
        if not warehouse_id:
            raise DataFormatError(f"Package entry missing warehouse reference: {entry!r}")
        packages.append(
            Package(
                id=entry["id"],
                warehouse_id=warehouse_id,
                destination=_as_coordinate(entry["destination"]),
            )
        )
    return packages


def load_delivery_data(path: str) -> Tuple[Dict[str, Warehouse], Dict[str, Agent], List[Package]]:
    """Read and parse a FastBox data file, returning normalized domain objects."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    for required_key in ("warehouses", "agents", "packages"):
        if required_key not in raw:
            raise DataFormatError(f"Input JSON is missing required key: '{required_key}'")

    raw_warehouses = _normalize_located_entities(raw["warehouses"], "warehouse")
    raw_agents = _normalize_located_entities(raw["agents"], "agent")
    packages = _normalize_packages(raw["packages"])

    warehouses = {wid: Warehouse(id=wid, location=loc) for wid, loc in raw_warehouses.items()}
    agents = {aid: Agent(id=aid, location=loc) for aid, loc in raw_agents.items()}

    # Cross-reference check: every package must point at a real warehouse.
    unknown = {p.warehouse_id for p in packages} - warehouses.keys()
    if unknown:
        raise DataFormatError(f"Packages reference unknown warehouse(s): {sorted(unknown)}")

    return warehouses, agents, packages
