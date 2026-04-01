# fieldtest-demo

A minimal working example of [fieldtest](https://github.com/gmitt98/fieldtest) in practice.

**The system:** A customer service email responder for a fictional store (ACME). Give it a policy document and a customer email — it generates a reply.

**The point:** A complete, runnable eval suite on something simple enough to understand in minutes — right/good/safe coverage, all four eval types, golden fixtures and variation fixtures.

---

## Prerequisites

- Python 3.10+
- An Anthropic API key (`sk-ant-...`)
- That's it

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/gmitt98/fieldtest-demo.git
cd fieldtest-demo

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...
```

> **Note:** The `source .venv/bin/activate` step must be run each time you open a new terminal window. You'll see `(.venv)` in your prompt when the environment is active.

Verify the eval config is valid:

```bash
fieldtest validate
```

Expected output:
```
✓ config valid: evals/config.yaml
  1 use case(s), 7 eval(s)
  by tag — right: 3, good: 2, safe: 2
  8 explicitly listed fixture(s)
```

---

## Run the eval

Two steps: run the system (generates outputs), then score (judges outputs).

### Step 1 — Run the system

```bash
# Smoke set: 2 fixtures × 3 runs each (fast, ~30 seconds)
python3 runner.py smoke

# Full set: 6 fixtures × 3 runs each (~2 minutes)
python3 runner.py full
```

You'll see output like:
```
use_case: email-response | set: smoke | 2 fixtures × 3 runs
  refund-eligible  run 1/3... ✓
  refund-eligible  run 2/3... ✓
  refund-eligible  run 3/3... ✓
  refund-ineligible-sale  run 1/3... ✓
  ...
```

Outputs land in `evals/outputs/{fixture-id}/run-{n}.txt`.

### Step 2 — Score

```bash
# Score the smoke set
fieldtest score smoke

# Or score the full set
fieldtest score full
```

Scoring runs the judges (LLM, regex, reference) against every output file and writes results to `evals/results/`.

### Step 3 — View the report

```bash
fieldtest view
```

Opens the HTML report in your browser. Shows tag health cards (RIGHT / GOOD / SAFE pass rates), a fixture × eval matrix, and per-run reasoning for every cell.

---

## What you'll see

Seven evals across three lenses:

| eval | tag | type | what it checks |
|------|-----|------|----------------|
| `addresses-the-ask` | RIGHT | llm | Did it answer the customer's actual question? |
| `policy-accurate` | RIGHT | llm | Are all policy claims correct per the store policy? |
| `golden-contains` | RIGHT | reference | Expected phrases present (golden fixtures only) |
| `appropriate-tone` | GOOD | llm | Warm, professional, proportionate to the situation? |
| `concise` | GOOD | llm | 2–5 sentences, no padding or truncation? |
| `no-unauthorized-commitments` | SAFE | llm | No promises beyond what the policy allows? |
| `no-policy-invention` | SAFE | regex | No invented policies (price match, loyalty points)? |

Six fixtures — two golden (with `expected` blocks that `golden-contains` checks), four variations (property-based evals only):

| fixture | type | scenario |
|---------|------|----------|
| `refund-eligible` | golden | In-window return, unused item, has receipt |
| `refund-ineligible-sale` | golden | Sale item — policy says no refunds |
| `damaged-item` | variation | Item arrived damaged — tests tone + commitment scope |
| `cancel-order` | variation | Order cancellation request |
| `international-shipping` | variation | Question about shipping to Canada |
| `vague-complaint` | variation | Frustrated customer, no specific ask |

---

## All commands

```bash
# Check config before running
fieldtest validate

# View previous runs
fieldtest history

# Compare two runs (default: most recent vs prior)
fieldtest diff

# Open HTML report (most recent run)
fieldtest view

# Delete all result files (keeps outputs/)
fieldtest clean
```

---

## What's in each file

```
app.py          — the system under test (policy + email → reply)
policy.txt      — ACME Store's business rules (the grounding document)
runner.py       — reads config, calls app.py for each fixture, writes outputs/
requirements.txt
evals/
  config.yaml           — system definition, evals, fixture sets
  fixtures/
    refund-eligible.yaml          ← golden (has expected block)
    refund-ineligible-sale.yaml   ← golden (has expected block)
    damaged-item.yaml             ← variation (no expected block)
    cancel-order.yaml             ← variation
    international-shipping.yaml   ← variation
    vague-complaint.yaml          ← variation
  outputs/              — written by runner.py (gitignored)
  results/              — written by fieldtest score (gitignored)
```

---

## A note on model IDs

This demo uses `claude-3-5-haiku-latest` in both `app.py` and `evals/config.yaml`. The `-latest` alias always resolves to the current stable version of the model, so the demo stays runnable as Anthropic releases new versions.

**Don't do this in a real eval suite.** Pin a specific model ID instead:

```yaml
# evals/config.yaml
defaults:
  model: claude-3-5-haiku-20241022  # pinned — behavior won't change under you
```

The `-latest` alias can silently point to a different model after an Anthropic release. If your evals pass today and fail next week, you won't know whether your system regressed or the model changed. Pinned IDs make runs reproducible and deltas meaningful.

---

## The /optimize skill

If you have [Claude Code](https://claude.ai/code) and the fieldtest `/optimize` command installed:

```
/optimize
```

The agent reads the failing evals, diagnoses which part of the prompt is responsible, edits `app.py`, re-runs the system, and re-scores. It loops until evals pass or the cycle limit is hit.

To install: copy `.claude/commands/optimize.md` from the [fieldtest repo](https://github.com/gmitt98/fieldtest) into this project's `.claude/commands/` directory.
