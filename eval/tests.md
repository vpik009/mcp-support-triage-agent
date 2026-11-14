# Evaluation results

How to run: `uv run python eval/run_eval.py dev` (or `test` / `all`). The script gives each ticket text from `data/tickets.jsonl` to the agent and checks its decisions against the labels. The wording of the reply is not scored. Per-ticket results (ids and decisions only, no message text) are saved to `eval/results_<split>.json`.

## Run 1: dev split, before any fixes

Date: 2026-11-14 · Model: qwen3:8b (Ollama, local GPU) · Retrieval: multilingual-e5-small, top 2 · 30 dev tickets

| Metric | Result |
|---|---|
| Category correct | 16 / 30 (53 %) |
| needs_human correct | 21 / 30 (70 %) |
| Ticket created exactly when a human is needed | 21 / 30 (70 %) |
| Medical questions sent to a human | 4 / 4 |
| Right FAQ entry used | 10 / 18 |
| Answered without a human (automation rate) | 5 / 30 (17 %), labels say 12 / 30 (40 %) |
| Average time per ticket | 5.3 s |

### What went wrong

- **Categories:** the model only sees the category names, not what they mean, and often falls back to `allgemein` (e.g. all three login and app tickets).
- **"Medical" triggers too easily:** questions that only mention a doctor or a document ("Muss ich einen Arztbrief einreichen?", "Wo lade ich meinen Ausweis hoch?") were treated as medical. This makes the agent over-cautious, so the automation rate is far below what the labels allow.
- **Human needed but no ticket:** in 8 tickets the agent decided a human must take over but never created a ticket, so in production nobody would see the request.
- **What works:** every medical question went to a human, and a ticket takes about 5 seconds.

### Possible fixes (not applied yet)

- Describe each category in one line in the system prompt.
- Define "medical" narrowly: health, dosage, side effects, symptoms, interactions. Not documents, appointments or doctor's letters.
- Guardrail in code: if `needs_human` is true and no ticket was created, create one from the final result.

## Run 2: model comparison on the dev split (same MCP server, same rules)

| Metric | qwen3:8b (local) | qwen3:4b (local) | Claude Opus 5.5 (cloud) |
|---|---|---|---|
| Category correct | 16 / 30 (53 %) | 18 / 30 (60 %) | TBA |
| needs_human correct | 21 / 30 (70 %) | 21 / 30 (70 %) | TBA |
| Ticket created exactly when a human is needed | 21 / 30 (70 %) | 25 / 30 (83 %) | TBA |
| Medical questions sent to a human | 4 / 4 | 4 / 4 | TBA |
| Right FAQ entry used | 10 / 18 | 15 / 18 | TBA |
| Answered without a human (automation rate) | 5 / 30 (17 %) | 9 / 30 (30 %) | TBA |
| Average time per ticket | 5.3 s | 39.3 s | TBA |
| Cost | none (local) | none (local) | TBA |
| Data leaves the machine | no | no | yes |

qwen3:4b was run once on the same 30 dev tickets (both runs fully on the RTX 3070, temperature 0). It scored better than qwen3:8b on most decisions but was about 7 times slower per ticket, with single tickets taking up to 2 minutes (probably more tool-call rounds and retries after wrong arguments, not checked in detail). With only 30 tickets and one run per model, small differences are not reliable.
