# fieldtest-demo

A minimal demo app showing [fieldtest](https://github.com/gmitt98/fieldtest) in practice.

**The app:** A customer service email responder for a fictional store. Give it a policy document and a customer email — it generates a reply.

**The point:** Show the complete fieldtest workflow on something simple enough to understand in minutes.

---

## What's here

```
app.py          — the system under test (two inputs → one output)
policy.txt      — the business context document
runner.py       — fieldtest runner (calls app.py, writes outputs/)
evals/
  config.yaml   — use cases, evals (right/good/safe), fixture sets
  fixtures/
    golden/     — fixtures with expected output checks
    variations/ — fixtures without expected checks
```

## Eval coverage

| eval | tag | type | what it checks |
|------|-----|------|----------------|
| addresses-the-ask | right | llm | Did it answer the customer's actual question? |
| policy-accurate | right | llm | Are all policy claims correct? |
| golden-contains | right | reference | Expected phrases present (golden fixtures) |
| appropriate-tone | good | llm | Warm, professional, proportionate? |
| concise | good | llm | 2–5 sentences, no padding? |
| no-unauthorized-commitments | safe | llm | No promises beyond what policy allows? |
| no-policy-invention | safe | regex | No invented policies (price match, loyalty points)? |

## Quickstart

```bash
# Install
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# Validate config
fieldtest validate

# Run the system (generates outputs/)
python runner.py smoke    # 2 fixtures
python runner.py full     # all 6 fixtures

# Score
fieldtest score smoke
fieldtest score full

# View history
fieldtest history

# Compare runs
fieldtest diff
```

## The /optimize skill

If you have [Claude Code](https://claude.ai/code) and the fieldtest `/optimize` command installed, you can run automated prompt optimization against these evals:

```
/optimize
```

The agent reads the failing evals, diagnoses which part of the prompt is responsible, edits `app.py`, re-runs the system, and re-scores. It loops up to N cycles (you set the threshold).

To install the optimize command, copy `.claude/commands/optimize.md` from the [fieldtest repo](https://github.com/gmitt98/fieldtest) into your project's `.claude/commands/` directory.
