# runs the agent on the labelled tickets and checks its decisions, not the wording of the reply
# run: uv run python eval/run_eval.py dev     (or test / all)
import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# eval tickets go to a throwaway outbox so they dont mix w/ the demo outbox
os.environ["OUTBOX_DIR"] = tempfile.mkdtemp(prefix="eval_outbox_")

from src.agent import MODEL, handle_message  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def summarize(rows):
    n = len(rows)
    cat_ok = 0
    human_ok = 0
    ticket_ok = 0
    medical = 0
    medical_caught = 0
    faq_total = 0
    faq_hits = 0
    auto = 0
    total_time = 0
    for r in rows:
        cat_ok += r["category"] == r["pred_category"]
        human_ok += r["needs_human"] == r["pred_needs_human"]
        ticket_ok += r["needs_human"] == r["made_ticket"]  # ticket exactly when a human is needed
        if r["category"] == "medizinisch":
            medical += 1
            medical_caught += r["pred_needs_human"]
        if r["faq_hit"] is not None:
            faq_total += 1
            faq_hits += r["faq_hit"]
        auto += not r["pred_needs_human"]
        total_time += r["seconds"]

    print()
    print("category correct:      ", cat_ok, "/", n, "=", round(100 * cat_ok / n), "%")
    print("needs_human correct:   ", human_ok, "/", n, "=", round(100 * human_ok / n), "%")
    print("ticket iff human needed:", ticket_ok, "/", n, "=", round(100 * ticket_ok / n), "%")
    print("medical sent to human: ", medical_caught, "/", medical)
    print("right faq used:        ", faq_hits, "/", faq_total)
    print("answered w/o human:    ", auto, "/", n, "=", round(100 * auto / n), "%  (automation rate)")
    print("avg time per ticket:   ", round(total_time / n, 1), "s")


async def main(split):
    tickets = []
    with open(ROOT / "data" / "tickets.jsonl", encoding="utf-8") as f:
        for line in f:
            t = json.loads(line)
            if split == "all" or t["split"] == split:
                tickets.append(t)
    print(len(tickets), "tickets,", split, "split,", MODEL)

    rows = []
    for t in tickets:
        start = time.time()
        out = await handle_message(t["text"])
        seconds = time.time() - start
        # print(t["id"], json.dumps(out, ensure_ascii=False)[:500])
        made_ticket = False
        for call in out["tool_calls"]:
            if call["tool"] == "create_jira_ticket" and "key" in str(call["result"]):
                made_ticket = True
        faq_hit = None
        if t["expected_faq"]:
            faq_hit = len(set(out["faq_ids"]) & set(t["expected_faq"])) > 0
        # only ids and decisions are stored, no message text
        rows.append({
            "id": t["id"], "category": t["category"], "pred_category": out["category"],
            "needs_human": t["needs_human"], "pred_needs_human": out["needs_human"],
            "made_ticket": made_ticket, "faq_hit": faq_hit, "seconds": round(seconds, 1),
        })
        ok = "ok " if out["category"] == t["category"] and out["needs_human"] == t["needs_human"] else "ERR"
        print(ok, t["id"], t["category"], "->", out["category"], "| human", t["needs_human"], "->", out["needs_human"],
              "| ticket", made_ticket, "|", round(seconds, 1), "s")

    summarize(rows)

    out_file = ROOT / "eval" / ("results_" + split + ".json")
    out_file.write_text(json.dumps(rows, indent=1))
    print("saved", out_file.name)


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "dev"
    asyncio.run(main(split))
