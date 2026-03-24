"""
runner.py — fieldtest runner for the ACME email responder

Reads fixtures from evals/config.yaml, calls app.py for each fixture,
writes outputs to evals/outputs/{fixture_id}/run-{n}.txt.

Conforms to the fieldtest runner contract.

Usage:
    python runner.py           # runs default set (full)
    python runner.py smoke     # runs smoke set only

Requires:
    pip install anthropic pyyaml fieldtest
    export ANTHROPIC_API_KEY=sk-ant-...
"""
import os
import sys
import pathlib
import yaml

# Import the system under test
from app import respond

POLICY_PATH = pathlib.Path("policy.txt")


def resolve_set(set_name: str, fixtures_cfg: dict, fixture_base: pathlib.Path) -> list[str]:
    sets  = fixtures_cfg.get("sets", {})
    value = sets.get(set_name)
    if value is None:
        print(f"Error: set '{set_name}' not found. Available: {list(sets.keys())}", file=sys.stderr)
        sys.exit(1)
    if value == "all":
        return [p.stem for p in sorted(fixture_base.rglob("*.yaml"))]
    if isinstance(value, str) and value.endswith("/*"):
        subdir = fixture_base / value[:-2]
        return [p.stem for p in sorted(subdir.glob("*.yaml"))]
    return value if isinstance(value, list) else []


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    config_path = pathlib.Path("evals/config.yaml")
    if not config_path.exists():
        print(f"Error: config not found at {config_path}", file=sys.stderr)
        sys.exit(1)

    policy = POLICY_PATH.read_text()
    config = yaml.safe_load(config_path.read_text())
    set_name = sys.argv[1] if len(sys.argv) > 1 else "full"

    for use_case in config["use_cases"]:
        fixtures_cfg = use_case["fixtures"]
        runs         = fixtures_cfg.get("runs") or config.get("defaults", {}).get("runs", 5)
        fixture_base = pathlib.Path("evals") / fixtures_cfg["directory"]
        fixture_ids  = resolve_set(set_name, fixtures_cfg, fixture_base)

        print(f"\nuse_case: {use_case['id']} | set: {set_name} | {len(fixture_ids)} fixtures × {runs} runs")

        for fixture_id in fixture_ids:
            fixture_path = fixture_base / f"{fixture_id}.yaml"
            try:
                fixture = yaml.safe_load(fixture_path.read_text())
            except Exception as e:
                print(f"Error loading fixture {fixture_path}: {e}", file=sys.stderr)
                sys.exit(1)

            customer_email = fixture["inputs"]["customer_email"]
            out_dir = pathlib.Path(f"evals/outputs/{fixture_id}")
            out_dir.mkdir(parents=True, exist_ok=True)

            for run in range(1, runs + 1):
                print(f"  {fixture_id}  run {run}/{runs}...", end=" ", flush=True)
                output = respond(policy, customer_email)
                (out_dir / f"run-{run}.txt").write_text(output)
                print("✓")


if __name__ == "__main__":
    main()
