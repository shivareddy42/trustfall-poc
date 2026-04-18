# TRUSTFALL

**A benchmark for evaluating LLM agent safety across composed enterprise system integrations.**

Pre-application POC (April 2026). Full research design in [`PRD.md`](./PRD.md).

---

## Why this exists

Every major agent safety benchmark — WebArena, AgentBench, τ-bench, AgentHarm, InjecAgent, ASB — evaluates agents in **one system with one tool surface**. Real enterprise deployments of agentic AI look nothing like that. A single agent routinely gets OAuth scopes into 5–15 systems (ITSM, procurement, CRM, email, identity, CMDB), and the transitive privilege graph of that federated scope is dramatically larger than the declared per-system scope.

TRUSTFALL measures what current benchmarks miss: agent safety *across* composed systems, with realistic governance (approval chains, RBAC, referential cascades), and with metrics that capture downstream propagation — **blast radius**, **reversibility**, **detection latency**, **transitive privilege ratio** — rather than just "did the agent misbehave."

## What's in this POC

A credible 2.5-week slice of the full benchmark:

- **CorpSim** — simulated enterprise environment spanning three systems (ITSM, procurement, email), 22 tool endpoints, shared state store with referential integrity, event bus, cascade engine, and a default SIEM rule set.
- **30 labeled adversarial scenarios** across three threat classes:
  - **T1 — Privilege Composition** (10 scenarios). Individually-authorized capabilities compose to unauthorized outcomes.
  - **T2 — Cascading State Corruption** (10 scenarios). A single write propagates via referential integrity across many records.
  - **T4 — Structured-Field Prompt Injection** (10 scenarios). Injections hidden inside schema-constrained enterprise data fields (vendor names, PO line items, approval notes). The most novel threat class in the corpus.
- **Harness** — tool dispatch loop, scope enforcement, full metric suite (ASR, BR, RI, DL, SWH, TPR).
- **Baseline runners** — OpenAI, Anthropic, and a deterministic MockRunner for offline testing.
- **Dashboard** — local web UI rendering event timelines, cascade trees, per-threat-class heatmaps, per-scenario TPR bars.
- **Smoke tests** — 4/4 passing with no API keys required.

## Early numbers (mock baseline)

From `python -m harness.run --model mock --scenarios all`:

| Threat class | n | mean TPR |
|---|---|---|
| T1 | 10 | 1.15× |
| T2 | 10 | 1.80× |
| T4 | 10 | 1.35× |
| **All** | **30** | **1.43×** |

**Transitive Privilege Ratio** is a static property of the agent's scope bundle — the count of reachable consequential actions divided by declared consequential actions. Even on this small POC corpus, **mean TPR = 1.43×**, meaning agents' effective consequential privilege averages 1.43× larger than what scope declarations suggest. Peak observed TPR = 3.00× (scenario T2-0009, user-email hijack). Full 1,200-scenario corpus should comfortably exceed the PRD's H1 hypothesis of ≥3× median. Frontier-model ASR/BR numbers on the POC coming before May 3.

## Quickstart

```bash
git clone https://github.com/shivareddy42/trustfall-poc
cd trustfall-poc
pip install pydantic pyyaml                             # minimum for offline smoke tests
python tests/smoke.py                                   # expect 4/4 passed

# For full harness + dashboard
pip install -e .
python -m harness.run --model mock --scenarios all --out results/mock.json
python -m dashboard.serve                               # http://127.0.0.1:8766
```

For frontier-model runs, set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` and swap `--model mock` for `--model gpt-5.3` or `--model claude-opus-4-7`.

## Repository layout

```
corpsim/         simulated enterprise environment (ITSM, Ariba, email, event bus, cascade engine)
scenarios/       30 labeled adversarial scenarios across T1, T2, T4
harness/         agent runner, metrics, CLI
baselines/       OpenAI + Anthropic + MockRunner
dashboard/       FastAPI + single-page dashboard
report/          preliminary findings writeup
tests/           offline smoke tests
PRD.md           full research design (target: OpenAI Safety Fellowship)
```

## What's deferred to the full fellowship build

Per [`PRD.md`](./PRD.md): a fourth simulator (CMDB/identity), 5 additional threat classes (T3, T5–T8), 1,170 additional scenarios, 5 reference mitigation architectures, a real-system calibration study against a live ServiceNow developer instance and SAP Ariba sandbox, and a public leaderboard.

## Status

| | |
|---|---|
| Scenarios | 30 / 1,200 (2.5%) |
| Simulators | 3 / 4 |
| Threat classes | 3 / 8 |
| Mitigations | 0 / 5 |
| Smoke tests | 4 / 4 passing |
| Frontier baselines | pending |

## License

MIT. See [`LICENSE`](./LICENSE).

## Contact

Shiva Reddy Peddireddy — [shivareddy42.github.io](https://shivareddy42.github.io) · [github.com/shivareddy42](https://github.com/shivareddy42)