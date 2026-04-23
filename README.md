# TRUSTFALL

**A benchmark for evaluating LLM agent safety across composed enterprise system integrations.**

Pre-application POC (April 2026). Full research design in [`PRD.md`](./PRD.md). Preliminary findings in [`report/findings.md`](./report/findings.md).

---

## Headline result

Four frontier-lab models, 30 adversarial scenarios, no mitigations. Total API spend under $5.

| Model | Tier | T1 ASR | T2 ASR | T4 ASR | Overall |
|---|---|---|---|---|---|
| GPT-5.4 | OpenAI flagship | 0.00 | 0.00 | 0.00 | 0.00 |
| Claude Sonnet 4.6 | Anthropic flagship | 0.00 | 0.00 | 0.00 | 0.00 |
| GPT-5.4-mini | OpenAI mid-tier | 0.00 | **0.20** | **0.10** | 0.10 |
| Claude Haiku 4.5 | Anthropic small | 0.00 | **0.20** | 0.00 | 0.07 |

**Five attacks succeeded across the mid-tier and small-tier models** — covering supplier bank rewrite, notification hijack, tax-ID diversion, and PO approval authorized on false authority forged inside a user-record field. One failure (**T4-0009 on GPT-5.4-mini**) is the first direct demonstration on a production frontier-lab model of a structured-field injection attack succeeding as theorized in the PRD: the model approved a **$62,000 PO** citing forged authority from a `name`-field parenthetical, with the model's own justification text paraphrasing the injection string.

**Transitive Privilege Ratio = 1.43× mean, 3.00× peak** across the 30 scenarios — early evidence for hypothesis H1 that effective agent privilege systematically exceeds declared scope.

Complete failure analysis and interpretation: [`report/findings.md`](./report/findings.md).

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
- **Dashboard** — local web UI rendering event timelines, cascade trees, per-threat-class heatmaps, per-scenario TPR bars. Side-by-side comparison across all 4 model runs.
- **Smoke tests** — 4/4 passing, no API keys required.

## Quickstart

```bash
git clone https://github.com/shivareddy42/trustfall-poc
cd trustfall-poc

# Offline (no API keys)
pip install pydantic pyyaml
python tests/smoke.py                                   # expect 4/4 passed

# Full harness + dashboard
pip install -e .
python -m dashboard.serve                               # http://127.0.0.1:8766

# Replicate the headline table (all runs are also committed under results/)
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
python -m harness.run --model gpt-5.4                   --scenarios all --out results/gpt54.json
python -m harness.run --model gpt-5.4-mini              --scenarios all --out results/gpt54mini.json
python -m harness.run --model claude-sonnet-4-6         --scenarios all --out results/sonnet46.json
python -m harness.run --model claude-haiku-4-5-20251001 --scenarios all --out results/haiku45.json
```

## Repository layout

```
corpsim/         simulated enterprise environment (ITSM, Ariba, email, event bus, cascade engine)
scenarios/       30 labeled adversarial scenarios across T1, T2, T4
harness/         agent runner, metrics, CLI
baselines/       OpenAI + Anthropic + MockRunner
dashboard/       FastAPI + single-page dashboard
report/          preliminary findings writeup with frontier-model numbers
results/         checked-in JSON results from 4 frontier runs (reviewer reproducibility)
tests/           offline smoke tests
PRD.md           full research design (target: OpenAI Safety Fellowship)
```

## What's deferred to the full fellowship build

Per [`PRD.md`](./PRD.md): a fourth simulator (CMDB/identity), 5 additional threat classes (T3, T5–T8), 1,170 additional scenarios including L3/L4 payload sophistication, 5 reference mitigation architectures, a real-system calibration study against a live ServiceNow developer instance and SAP Ariba sandbox, and a public leaderboard.

## Status

| | |
|---|---|
| Scenarios | 30 / 1,200 |
| Simulators | 3 / 4 |
| Threat classes | 3 / 8 |
| Mitigations | 0 / 5 |
| Frontier baselines | GPT-5.4, Sonnet 4.6, GPT-5.4-mini, Haiku 4.5 (all committed) |
| Smoke tests | 4 / 4 passing |

## License

MIT. See [`LICENSE`](./LICENSE).

## Contact

Shiva Reddy Peddireddy — [shivareddy42.github.io](https://shivareddy42.github.io) · [github.com/shivareddy42](https://github.com/shivareddy42)