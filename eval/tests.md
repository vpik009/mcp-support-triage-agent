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

### Possible fixes

- Describe each category in one line in the system prompt.
- Define "medical" narrowly: health, dosage, side effects, symptoms, interactions. Not documents, appointments or doctor's letters.
- Guardrail in code: if `needs_human` is true and no ticket was created, create one from the final result. **Applied on 2026-11-15** (`handle_message` in `src/agent.py`, tickets get the label `auto_ticket`). The tables on this page are from before this change.

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

## Run 3: qwen3:8b with the auto ticket (dev split)

Date: 2026-11-15 · Same setup as run 1, plus the guardrail in `handle_message`: if `needs_human` is true and the model created no ticket, the code creates one (label `auto_ticket`).

| Metric | Run 1 (before) | Run 3 (auto ticket) |
|---|---|---|
| Category correct | 16 / 30 (53 %) | 15 / 30 (50 %) |
| needs_human correct | 21 / 30 (70 %) | 21 / 30 (70 %) |
| Ticket created exactly when a human is needed | 21 / 30 (70 %) | 21 / 30 (70 %) |
| Human needed (by the agent's decision) but no ticket | 8 | 0 |
| Medical questions sent to a human | 4 / 4 | 4 / 4 |
| Right FAQ entry used | 10 / 18 | 10 / 18 |
| Answered without a human (automation rate) | 5 / 30 (17 %) | 5 / 30 (17 %) |
| Average time per ticket | 5.3 s | 5.4 s |

- No request the agent hands over is lost anymore: a ticket now exists exactly when the agent says a human is needed.
- The ticket score did not move, because the remaining 9 mismatches are wrong decisions, not forgotten tickets: 8 unneeded tickets (ids 10, 26, 34, 37, 38, 49, 74, 81; 37 and 38 wrongly classed as medical) and 1 missed handover (id 67, an app problem the agent tried to answer itself).
- So the next fixes are about the decision itself: category descriptions and a narrower definition of "medical".
- Category correct dropped by one ticket (16 to 15) although the guardrail does not touch the category. Probably run-to-run noise: GPU inference is not fully deterministic even at temperature 0.
- `results_dev.json` now holds this run.

## Run 4: qwen3:4b with the auto ticket (dev split)

Date: 2026-11-15 · Same code as run 3, model switched to qwen3:4b.

| Metric | qwen3:8b (run 3) | qwen3:4b (run 4) |
|---|---|---|
| Category correct | 15 / 30 (50 %) | 18 / 30 (60 %) |
| needs_human correct | 21 / 30 (70 %) | 21 / 30 (70 %) |
| Ticket created exactly when a human is needed | 21 / 30 (70 %) | 22 / 30 (73 %) |
| Medical questions sent to a human | 4 / 4 | 4 / 4 |
| Right FAQ entry used | 10 / 18 | 15 / 18 |
| Answered without a human (automation rate) | 5 / 30 (17 %) | 9 / 30 (30 %) |
| Average time per ticket | 5.4 s | 40.4 s (max 127.5 s) |

- 4b still decides better on category, FAQ use and automation rate, and is still about 7 times slower.
- Ticket mismatches for 4b: 6 unneeded tickets (ids 17, 34, 37, 38, 74, 81; 17, 37 and 38 wrongly classed as medical) and 2 missed handovers (ids 54, 67).
- The ticket score for 4b is lower than in run 2 (83 % there, 73 % here). Likely reason: the auto ticket also creates a ticket when the model wrongly says a human is needed, which counts as an unneeded ticket. Run-to-run noise may add to it. Not checked in detail, since the results file does not record which tickets were auto tickets.
- The log shows several invalid tool calls from 4b (wrong argument names for `get_order_status` and `notify_slack`), which fits the guess that it needs more tool rounds and is slower because of that.
- `results_dev.json` now holds this run.
