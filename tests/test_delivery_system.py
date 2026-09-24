import json
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.assignment import assign_packages
from src.data_loader import DataFormatError, load_delivery_data
from src.distance import euclidean
from src.simulation import build_report, simulate_deliveries

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def sample_data_path():
    return os.path.join(os.path.dirname(__file__), "..", "data.json")


def test_euclidean_distance_basic():
    assert euclidean((0, 0), (3, 4)) == pytest.approx(5.0)
    assert euclidean((5, 5), (5, 5)) == 0.0


def test_load_dict_format(sample_data_path):
    warehouses, agents, packages = load_delivery_data(sample_data_path)
    assert set(warehouses) == {"W1", "W2", "W3"}
    assert set(agents) == {"A1", "A2", "A3"}
    assert len(packages) == 5
    assert warehouses["W2"].location == (50.0, 75.0)


def test_load_list_format(tmp_path):
    data = {
        "warehouses": [{"id": "W1", "location": [0, 0]}],
        "agents": [{"id": "A1", "location": [1, 1]}],
        "packages": [{"id": "P1", "warehouse_id": "W1", "destination": [5, 5]}],
    }
    p = tmp_path / "list_format.json"
    p.write_text(json.dumps(data))
    warehouses, agents, packages = load_delivery_data(str(p))
    assert warehouses["W1"].location == (0.0, 0.0)
    assert packages[0].warehouse_id == "W1"


def test_load_rejects_unknown_warehouse(tmp_path):
    data = {
        "warehouses": {"W1": [0, 0]},
        "agents": {"A1": [1, 1]},
        "packages": [{"id": "P1", "warehouse": "W9", "destination": [5, 5]}],
    }
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data))
    with pytest.raises(DataFormatError):
        load_delivery_data(str(p))


def test_load_rejects_missing_key(tmp_path):
    p = tmp_path / "bad2.json"
    p.write_text(json.dumps({"warehouses": {}, "agents": {}}))
    with pytest.raises(DataFormatError):
        load_delivery_data(str(p))


def test_assignment_picks_nearest_agent(sample_data_path):
    warehouses, agents, packages = load_delivery_data(sample_data_path)
    assign_packages(warehouses, agents, packages)
    # P1 & P4 come from W1, which A1 (5,5) is unambiguously closest to.
    assert next(p for p in packages if p.id == "P1").assigned_agent == "A1"
    assert next(p for p in packages if p.id == "P4").assigned_agent == "A1"
    # P2 & P5 come from W2, which A2 (60,60) is closest to.
    assert next(p for p in packages if p.id == "P2").assigned_agent == "A2"
    # P3 comes from W3, which A3 (95,30) is closest to.
    assert next(p for p in packages if p.id == "P3").assigned_agent == "A3"


def test_assignment_tie_break_deterministic():
    from src.models import Agent, Warehouse, Package

    warehouses = {"W1": Warehouse("W1", (0, 0))}
    # Both agents exactly 5 units from the warehouse -> tie.
    agents = {"AZ": Agent("AZ", (5, 0)), "AA": Agent("AA", (0, 5))}
    packages = [Package("P1", "W1", (10, 10))]
    assign_packages(warehouses, agents, packages)
    assert packages[0].assigned_agent == "AA"  # lexicographically smallest wins


def test_simulation_all_packages_delivered(sample_data_path):
    warehouses, agents, packages = load_delivery_data(sample_data_path)
    assign_packages(warehouses, agents, packages)
    reports, best_agent = simulate_deliveries(warehouses, agents, packages)
    total_delivered = sum(r.packages_delivered for r in reports.values())
    assert total_delivered == len(packages) == 5
    assert best_agent is not None


def test_efficiency_formula_matches_brief_example():
    # Reproduces the exact relationship shown in the assignment brief:
    # efficiency = total_distance / packages_delivered, lower = better.
    from src.models import AgentReport

    r = AgentReport(agent_id="A1", packages_delivered=2, total_distance=85.32)
    r.efficiency = r.total_distance / r.packages_delivered
    assert r.efficiency == pytest.approx(42.66, abs=0.01)


def test_agent_with_zero_packages_is_not_best(sample_data_path):
    from src.models import Agent

    warehouses, agents, packages = load_delivery_data(sample_data_path)
    agents["A4_idle"] = Agent("A4_idle", (1000, 1000))  # far away, will get 0 packages
    assign_packages(warehouses, agents, packages)
    reports, best_agent = simulate_deliveries(warehouses, agents, packages)
    assert reports["A4_idle"].packages_delivered == 0
    assert reports["A4_idle"].efficiency == 0.0
    assert best_agent != "A4_idle"


def test_build_report_shape(sample_data_path):
    warehouses, agents, packages = load_delivery_data(sample_data_path)
    assign_packages(warehouses, agents, packages)
    reports, best_agent = simulate_deliveries(warehouses, agents, packages)
    report = build_report(reports, best_agent)
    assert "best_agent" in report
    for agent_id in agents:
        assert set(report[agent_id].keys()) == {"packages_delivered", "total_distance", "efficiency"}


def test_official_test_cases_all_parse_and_balance():
    """Every officially supplied test_case_*.json must load, assign,
    simulate, and deliver exactly as many packages as were input."""
    tc_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "assignment",
        "Python Assignment(Delivery System Test Cases)",
    )
    if not os.path.isdir(tc_dir):
        pytest.skip("Official test case fixtures not present in this environment.")
    for fname in sorted(os.listdir(tc_dir)):
        if not fname.endswith(".json"):
            continue
        warehouses, agents, packages = load_delivery_data(os.path.join(tc_dir, fname))
        assign_packages(warehouses, agents, packages)
        reports, best_agent = simulate_deliveries(warehouses, agents, packages)
        total_delivered = sum(r.packages_delivered for r in reports.values())
        assert total_delivered == len(packages), f"{fname}: package count mismatch"
