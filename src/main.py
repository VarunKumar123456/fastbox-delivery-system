"""
FastBox Mystery Delivery System - CLI entrypoint.

Usage:
    python -m src.main --input data.json --output report.json
    python -m src.main --input data.json --output report.json --ascii-map
    python -m src.main --input data.json --output report.json --delays --seed 42
    python -m src.main --input data.json --output report.json --export-top top_performer.csv

Exit codes: 0 on success, 1 on any input/data error (with a clear
message on stderr) so this is CI/script friendly.
"""

import argparse
import json
import sys
from typing import Dict, Optional

from .assignment import assign_packages
from .bonus import export_top_performer_csv, render_ascii_map
from .data_loader import DataFormatError, load_delivery_data
from .simulation import build_report, simulate_deliveries


def run(
    input_path: str,
    output_path: str,
    show_ascii_map: bool = False,
    apply_delays: bool = False,
    seed: Optional[int] = None,
    export_top_csv: Optional[str] = None,
) -> Dict[str, object]:
    warehouses, agents, packages = load_delivery_data(input_path)

    assign_packages(warehouses, agents, packages)
    reports, best_agent = simulate_deliveries(
        warehouses, agents, packages, apply_random_delays=apply_delays, random_seed=seed
    )
    report = build_report(reports, best_agent)

    # Sanity check called out explicitly in the brief's notes.
    total_delivered = sum(
        r["packages_delivered"]  # type: ignore[index]
        for k, r in report.items()
        if k != "best_agent"
    )
    if total_delivered != len(packages):
        raise AssertionError(
            f"Integrity check failed: {total_delivered} packages reported delivered, "
            f"but {len(packages)} packages were in the input."
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if show_ascii_map:
        print(render_ascii_map(warehouses, agents, packages))
        print()

    if export_top_csv and best_agent:
        export_top_performer_csv(reports, best_agent, export_top_csv)
        print(f"Top performer ({best_agent}) exported to {export_top_csv}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="FastBox Mystery Delivery System simulator")
    parser.add_argument("--input", default="data.json", help="Path to input JSON (default: data.json)")
    parser.add_argument("--output", default="report.json", help="Path to write the report JSON (default: report.json)")
    parser.add_argument("--ascii-map", action="store_true", help="Bonus: print an ASCII route map")
    parser.add_argument("--delays", action="store_true", help="Bonus: simulate random per-package delivery delays")
    parser.add_argument("--seed", type=int, default=None, help="Random seed, for reproducible --delays output")
    parser.add_argument("--export-top", metavar="CSV_PATH", help="Bonus: export the top performer's stats to a CSV file")
    args = parser.parse_args()

    try:
        report = run(
            input_path=args.input,
            output_path=args.output,
            show_ascii_map=args.ascii_map,
            apply_delays=args.delays,
            seed=args.seed,
            export_top_csv=args.export_top,
        )
    except (DataFormatError, FileNotFoundError, AssertionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(report, indent=2))
    print(f"\nReport written to {args.output}")


if __name__ == "__main__":
    main()
