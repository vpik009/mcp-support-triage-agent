# mcp-support-triage-agent

A local LLM agent that triages patient support messages. It sorts each message into a support category and answers it from a FAQ when the FAQ covers the question. Otherwise it creates a Jira ticket, and for medical questions also posts to Slack, so that a person takes over. The tools sit behind a small MCP server of its own, so the same tools work with a local Qwen3 model on Ollama and with Claude Code.

I built it as a case study for the patient support team of a German medical cannabis telemedicine company, with Bloomwell's public FAQ as example data. The project is not affiliated with Bloomwell. All support messages, orders and personal data in this repo are invented.

## What the agent does

For each incoming message (German), the agent:

1. searches the FAQ and, if the message mentions an order or tracking number, looks up the order
2. decides whether the FAQ fully answers the question
3. hands the message to a human if it is a medical question, a complaint, a request that needs a real action (refund, change after payment, data deletion) or a question the FAQ does not answer, in which case it creates a Jira ticket and, for medical questions, also notifies `#medical-ops` on Slack
4. returns a JSON result with `category`, `needs_human`, `reason`, `faq_ids` and a short German reply in the formal "Sie" form that ends with the FAQ source URL

Medical questions always go to a human. The system prompt says so, and the code enforces it as well: if the category is `medizinisch`, `needs_human` is set to true whatever the model returned.

## How it works

```
support message
  -> src/agent.py        Qwen3 on Ollama, tool loop (max 6 steps)
       -> src/mcp_server.py   FastMCP server with 4 tools
            search_faq          multilingual-e5-small embeddings, cosine similarity, top 2
            get_order_status    mock order API (data/mock_orders.json)
            create_jira_ticket  -> backend: file outbox or Jira REST API
            notify_slack        -> backend: file outbox
  -> final call w/o tools, answer forced into a fixed JSON schema
  -> medical rule applied in code
```

Some decisions behind it:

- **Local LLM.** Support messages contain health and personal data. Since the model runs locally with Ollama, nothing leaves the machine, so the prototype has no pseudonymisation layer. That layer becomes necessary as soon as a cloud model is used, and the test data already marks every piece of personal data (`pii` field) so it can be measured later.
- **Own MCP server instead of the official Atlassian one.** It runs without any accounts and keeps the evaluation offline and repeatable. Test runs also don't create real tickets. The default file backend writes the same fields the Jira REST API expects to `outbox/jira.jsonl` and returns keys like `SUP-101`. With `BACKEND=jira` the same fields go to a real Jira Cloud site. That path is written but not yet tested against a live site.
- **No similarity threshold.** On the dev set, the best scores for messages with a fitting FAQ entry (0.81 to 0.93) overlap with those for messages where nothing fits (0.82 to 0.88). Similarity is therefore only used for ranking, and the LLM decides whether the retrieved entries answer the question. Retrieval puts the right entry in the top 3 for 16 of 18 dev messages (top 1: 13 of 18).
- **Real support categories.** The labels come from the categories on Bloomwell's support form, plus one extra category, `medizinisch`, which is never answered automatically.

## Data

| File | Content |
|---|---|
| `data/faq.json` | 31 FAQ entries, paraphrased in German from Bloomwell's public website, each with category, source URL and retrieval date (2026-11-14) |
| `data/tickets.jsonl` | 100 synthetic German support messages with labels: category, needs_human, reason, expected FAQ entries, personal data, split |
| `data/tickets_review.md` | the same 100 messages as a table for checking labels by hand |
| `data/mock_orders.json` | 6 invented orders whose order and tracking numbers match the test messages |
| `data/faq_vectors.npy` | precomputed FAQ embeddings. Delete the file after changing the FAQ and it is rebuilt on the next search |

48 of the 100 messages need a human (12 medical, 15 action, 14 no FAQ, 7 complaints). Some are hard on purpose, for example a medical question hidden after "Paket ist angekommen, danke!" or an address change that the FAQ explains but that still needs a person because the order is already paid. The messages are split 30 dev / 70 test, stratified by category with a fixed seed. Prompts are tuned on dev only.

## Setup

You need Python 3.11 or 3.12, [uv](https://docs.astral.sh/uv/) and [Ollama](https://ollama.com). A GPU is optional but makes the LLM much faster. I developed it on an RTX 3070 with 8 GB.

```bash
git clone https://github.com/<your-user>/mcp-support-triage-agent.git
cd mcp-support-triage-agent
uv sync
ollama pull qwen3:8b
```

The embedding model (`intfloat/multilingual-e5-small`) is downloaded from Hugging Face on the first search. PyTorch is installed as the CPU build, which is fast enough for 31 FAQ entries and leaves the GPU to the LLM.

## Usage

### Local agent

```bash
uv run python -m src.agent
```

Type a support message at the prompt, for example `Mein Paket BW-2026-49120 bewegt sich seit 9 Tagen nicht.` The agent prints each tool call and then the category, `needs_human`, the FAQ entries used and the reply. Tickets and Slack messages end up in `outbox/jira.jsonl` and `outbox/slack.jsonl`.

### With Claude Code

The repo contains a `.mcp.json` that registers the server as `bloomwell-support`. Start `claude` in the repo folder and approve the server when asked. The four tools then show up as `mcp__bloomwell-support__search_faq` and so on, and Claude Code can triage messages with the same tools and the same outbox.

To run the server on its own (stdio): `uv run python -m src.mcp_server`

### Real Jira (optional)

Use a separate test site, not a production Jira, with a project that has the key `SUP`.

```bash
export BACKEND=jira
export JIRA_URL=https://<your-site>.atlassian.net
export JIRA_EMAIL=<your-email>
export JIRA_API_TOKEN=<your-token>
```

Slack messages still go to the outbox file in this mode.

## Evaluation

```bash
uv run python eval/run_eval.py dev      # or test / all
```

The script runs the agent on the labelled messages and checks only its decisions (category, `needs_human`, whether a ticket was created, which FAQ entries were used), not the wording of the reply. Per-message results are saved to `eval/results_<split>.json` with ids and decisions only, no message text.

Results on the 30 dev messages, before any prompt fixes:

| Metric | qwen3:8b (local) | qwen3:4b (local) | Claude Opus 5.5 (cloud) |
|---|---|---|---|
| Category correct | 16 / 30 (53 %) | 18 / 30 (60 %) | TBA |
| needs_human correct | 21 / 30 (70 %) | 21 / 30 (70 %) | TBA |
| Ticket created exactly when a human is needed | 21 / 30 (70 %) | 25 / 30 (83 %) | TBA |
| Medical questions sent to a human | 4 / 4 | 4 / 4 | TBA |
| Right FAQ entry used | 10 / 18 | 15 / 18 | TBA |
| Answered without a human (automation rate) | 5 / 30 (17 %) | 9 / 30 (30 %) | TBA |
| Average time per message | 5.3 s | 39.3 s | TBA |
| Data leaves the machine | no | no | yes |

The labels allow an automation rate of 12 / 30 (40 %). qwen3:4b made better decisions than qwen3:8b on most metrics but was about 7 times slower, probably because of more tool-call rounds and retries after wrong arguments (not checked in detail). With 30 messages and one run per model, small differences are not reliable. The test split has not been run yet and is kept for one final run.

The main errors with qwen3:8b: the model only sees the category names and often falls back to `allgemein`. It also treats questions as medical when they only mention a doctor's letter or an ID document. Finally, in 8 messages it decided that a human must take over but never created a ticket, so in production nobody would see the request. Details and possible fixes are in [eval/tests.md](eval/tests.md).

## Limitations and next steps

- Fixes found in the evaluation are not applied yet: a one-line description per category, a narrower definition of "medical" and a guardrail in code that creates a ticket whenever `needs_human` is true and the model did not create one.
- The Jira backend has not been tested against a live site.
- There is no pseudonymisation layer, which a cloud model would need.
- The dev set is small (30 messages), and the replies themselves are not scored.

## Repo layout

```
src/
  agent.py         local agent: MCP client + Ollama tool loop
  mcp_server.py    MCP server with the 4 tools
  tools.py         FAQ search, order lookup, ticket and Slack logic
  backends.py      file outbox and Jira REST backend
data/              FAQ, synthetic messages, mock orders, FAQ embeddings
eval/
  run_eval.py      evaluation with the local agent
  tests.md         results and error analysis
.mcp.json          registers the MCP server for Claude Code
```
