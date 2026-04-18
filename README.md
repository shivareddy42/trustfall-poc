# TRUSTFALL — POC

Preliminary prototype for a benchmark measuring LLM agent safety across composed enterprise system integrations.

**Status:** Pre-application POC (targeting May 3, 2026). Not the full benchmark — a credible slice across 3 threat classes and 2 simulated systems.

## What's here

- `corpsim/` — Simulated enterprise systems (ITSM, Procurement) with an event bus and cascade engine
- `scenarios/` — Labeled adversarial scenarios across threat classes T1 (Privilege Composition), T2 (Cascading State Corruption), T4 (Structured-Field Injection)
- `harness/` — Agent runner + metrics (ASR, Blast Radius, Reversibility Index, Detection Latency)
- `baselines/` — Frontier model runners (OpenAI, Anthropic)
- `dashboard/` — Local visualization of results
- `report/` — Preliminary findings writeup

## Quickstart

```bash
pip install -e .
python -m corpsim.serve          # starts simulated enterprise on :8765
python -m harness.run --model gpt-5.3 --scenarios all
python -m dashboard.serve        # results viewer on :8766
```

## Full research plan

See `PRD.md` (TRUSTFALL v0.1) for the full research design. This repo implements Appendix B of the PRD.

## License

MIT. See `LICENSE`.
