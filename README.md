# TRUSTFALL

**A benchmark for evaluating LLM agent safety across composed enterprise system integrations.**

Pre-application POC (April 2026). Full research design in [`PRD.md`](./PRD.md). Preliminary findings in [`report/findings.md`](./report/findings.md).

---

## Why this exists

Every major agent safety benchmark — WebArena, AgentBench, τ-bench, AgentHarm, InjecAgent, ASB — evaluates agents in **one system with one tool surface**. Real enterprise deployments of agentic AI look nothing like that. A single agent routinely gets OAuth scopes into 5–15 systems (ITSM, procurement, CRM, email, identity, CMDB), and the transitive privilege graph of that federated scope is dramatically larger than the declared per-system scope.

TRUSTFALL measures what current benchmarks miss: agent safety *across* composed systems, with realistic governance (approval chains, RBAC, referential cascades), and with metrics that capture downstream propagation — **blast radius**, **reversibility**, **detection latency**, **transitive privilege ratio** — rather than just "did the agent misbehave."

## What's in this POC

- **CorpSim** — simulated enterprise environment spanning three systems (ITSM, procurement, email), 22 tool endpoints, shared state store with referential integrity, event bus, cascade engine, and a default SIEM rule set.
- **30 labeled adversarial scenarios** across three threat classes:
  - **T1 — Privilege Composition** (10 scenarios)
  - **T2 — Cascading State Corruption** (10 scenarios)
  - **T4 — Structured-Field Prompt Injection** (10 scenarios)
- **Harness** — tool dispatch loop, scope enforcement, full metric suite (ASR, BR, RI, DL, SWH, TPR).
- **Baseline runners** — OpenAI, Anthropic, and a deterministic MockRunner for offline testing.
- **Dashboard** — local web UI rendering event timelines, cascade trees, per-threat-class heatmaps, per-scenario TPR bars.
- **Smoke tests** — 4/4 passing, no API keys required.

## Frontier-model results (April 2026)

Both models, all 30 scenarios, no mitigations:

| Threat class | n | GPT-5.4 ASR | Sonnet 4.6 ASR | mean TPR |
|---|---|---|---|---|
| T1 — Privilege Composition | 10 | 0.00 | 0.00 | 1.15 |
| T2 — Cascading State Corruption | 10 | 0.00 | 0.00 | 1.80 |
| T4 — Structured-Field Injection | 10 | 0.00 | 0.00 | 1.35 |
| **Overall** | **30** | **0.00** | **0.00** | **1.43** |

**ASR = 0.00 across the board is a real finding, not a silent-failure artifact.** Engagement diagnostics: GPT-5.4 averaged 2.3 tool calls/scenario (70 total invocations, 3 zero-call scenarios); Sonnet 4.6 averaged 3.5 (104 invocations, 0 zero-call scenarios). Both models investigate before refusing. A per-invocation audit of every write-class action confirmed zero harmful actions slipped past the harness. Full analysis in [`report/findings.md`](./report/findings.md).

**What this means:** current frontier safety tuning correctly handles L1–L2 attack sophistication on this POC corpus. The full benchmark needs L3–L4 adversarial payloads within the same threat classes — this is the highest-priority corpus-expansion axis for the fellowship.

**Transitive Privilege Ratio = 1.43× mean, 3.00× max.** Early evidence for PRD hypothesis H1: declared scope is systematically narrower than effective scope even in this small corpus.

## Quickstart

```bash
git clone https://github.com/shivareddy42/trustfall-poc
cd trustfall-poc

# Offline (no API keys)
pip install pydantic pyyaml
python tests/smoke.py                                   # expect 4/4 passed

# Full harness + dashboard
pip install -e .
python -m harness.run --model mock --scenarios all --out results/mock.json
python -m dashboard.serve                               # http://127.0.0.1:8766

# With API keys
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
python -m harness.run --model gpt-5.4          --scenarios all --out results/gpt54.json
python -m harness.run --model claude-sonnet-4-6 --scenarios all --out results/sonnet46.json
```

## Repository layout

```
corpsim/         simulated enterprise environment (ITSM, Ariba, email, event bus, cascade engine)
scenarios/       30 labeled adversarial scenarios across T1, T2, T4
harness/         agent runner, metrics, CLI
baselines/       OpenAI + Anthropic + MockRunner
dashboard/       FastAPI + single-page dashboard
report/          preliminary findings writeup with frontier-model numbers
results/         checked-in JSON results from frontier runs (reviewer reproducibility)
tests/           offline smoke tests
PRD.md           full research design (target: OpenAI Safety Fellowship)
```

## What's deferred to the full fellowship build

Per [`PRD.md`](./PRD.md): a fourth simulator (CMDB/identity), 5 additional threat classes (T3, T5–T8), 1,170 additional scenarios including L3/L4 payload sophistication, 5 reference mitigation architectures, a real-system calibration study against a live ServiceNow developer instance and SAP Ariba sandbox, and a public leaderboard.

## Status

| | |
|---|---|
| Scenarios | 30 / 1,200 (2.5%) |
| Simulators | 3 / 4 |
| Threat classes | 3 / 8 |
| Mitigations | 0 / 5 |
| Frontier baselines | GPT-5.4 + Claude Sonnet 4.6 (ASR 0.00 / 30 each) |
| Smoke tests | 4 / 4 passing |

## License

MIT. See [`LICENSE`](./LICENSE).

## Contact

Shiva Reddy Peddireddy — [shivareddy42.github.io](https://shivareddy42.github.io) · [github.com/shivareddy42](https://github.com/shivareddy42)
