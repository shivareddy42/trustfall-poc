"""Command-line runner.

Usage:
  python -m harness.run --model mock --scenarios all
  python -m harness.run --model gpt-5.3 --scenarios t1 --out results/gpt53_t1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from corpsim.common.scenarios import load_all_scenarios, Scenario
from harness.runner import run_scenario, ScenarioRun
from harness.metrics import compute_metrics, aggregate, RunMetrics


ROOT = Path(__file__).resolve().parent.parent


def _build_runner(model: str):
    if model == "mock":
        # Default mock: always stops immediately with no action. Useful as baseline.
        from baselines import MockRunner
        return MockRunner(script=[{"content": "no action", "tool_calls": [], "stop": True}],
                          name="mock-noop")
    if model.startswith("gpt") or model.startswith("openai"):
        from baselines import OpenAIRunner
        return OpenAIRunner(model=model)
    if model.startswith("claude") or model.startswith("anthropic"):
        from baselines import AnthropicRunner
        return AnthropicRunner(model=model)
    raise ValueError(f"unknown model: {model}")


def _filter_scenarios(scenarios: list[Scenario], filt: str) -> list[Scenario]:
    if filt == "all":
        return scenarios
    prefix = filt.upper()
    return [s for s in scenarios if s.threat_class == prefix
            or s.id.startswith(prefix)]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="mock")
    p.add_argument("--scenarios", default="all",
                   help="'all' or threat class 'T1' / 'T2' / 'T4' or scenario prefix")
    p.add_argument("--provider", default="openai", choices=["openai", "anthropic"],
                   help="Message-format provider. Use anthropic for claude models.")
    p.add_argument("--out", default=None, help="Write results JSON to this path")
    p.add_argument("--scenarios-dir", default=str(ROOT / "scenarios"))
    args = p.parse_args()

    scenarios = load_all_scenarios(args.scenarios_dir)
    scenarios = _filter_scenarios(scenarios, args.scenarios)
    if not scenarios:
        print(f"No scenarios matched {args.scenarios}")
        return 1

    # Auto-detect provider from model if not specified explicitly
    provider = args.provider
    if args.model.startswith("claude") or args.model.startswith("anthropic"):
        provider = "anthropic"

    runner = _build_runner(args.model)
    all_runs: list[ScenarioRun] = []
    all_metrics: list[RunMetrics] = []

    for i, scen in enumerate(scenarios, 1):
        print(f"[{i}/{len(scenarios)}] {scen.id} ({scen.threat_class}) ", end="", flush=True)
        try:
            # Rebuild runner for each scenario if it's MockRunner (script depletes)
            if args.model == "mock":
                runner = _build_runner("mock")
            run = run_scenario(scen, runner, provider=provider)
            m = compute_metrics(scen, run)
            all_runs.append(run)
            all_metrics.append(m)
            flag = "ATTACK" if m.attack_success else "safe"
            print(f"{flag} BR={m.blast_radius} TPR={m.transitive_privilege_ratio:.2f}")
        except Exception as e:
            print(f"ERROR: {e}")

    # Aggregate
    print("\n=== Aggregate ===")
    for agg in aggregate(all_metrics):
        print(f"{agg.model} {agg.threat_class} n={agg.n} "
              f"ASR={agg.asr:.2f} BR={agg.mean_blast_radius:.1f} "
              f"RI={agg.mean_reversibility:.2f} "
              f"DL={agg.mean_detection_latency} "
              f"SWH={agg.mean_swh:.2f} TPR={agg.mean_tpr:.2f}")

    # Write results
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": args.model,
            "scenarios": args.scenarios,
            "runs": [_run_to_dict(r) for r in all_runs],
            "metrics": [asdict(m) for m in all_metrics],
            "aggregates": [asdict(a) for a in aggregate(all_metrics)],
        }
        out_path.write_text(json.dumps(payload, indent=2, default=str))
        print(f"\nWrote {out_path}")

    return 0


def _run_to_dict(run: ScenarioRun) -> dict:
    return {
        "scenario_id": run.scenario_id,
        "threat_class": run.threat_class,
        "model": run.model,
        "turns": run.turns,
        "final_text": run.final_text[:2000],
        "terminated_by": run.terminated_by,
        "error": run.error,
        "wall_ms": run.wall_ms,
        "invocations": [
            {"tool": i.tool, "args": i.args, "error": i.error,
             "duration_ms": i.duration_ms,
             "result_preview": str(i.result)[:500] if i.result is not None else None}
            for i in run.invocations
        ],
        "events": run.events,
    }


if __name__ == "__main__":
    sys.exit(main())
