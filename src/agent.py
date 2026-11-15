# local support agent (qwen3 on ollama + mcp tools), run: uv run python -m src.agent
import asyncio
import json
import sys
from pathlib import Path

import ollama
from dotenv import load_dotenv
from fastmcp import Client

from src.mcp_server import mcp
from src.tools import CATEGORIES

MODEL = "qwen3:8b"
MAX_STEPS = 6  # stops the loop if the model keeps calling tools

SYSTEM_PROMPT = """You are an assistant for the Bloomwell patient support team (medical cannabis telemedicine, Germany).
You get one incoming support message from a patient. Your job:
1. Call search_faq with the patient's question. If the message mentions an order or tracking number, call get_order_status.
2. Decide if the FAQ answers the question fully. Only use what the FAQ entries say, never invent facts.
3. A human must take over if: it is a medical question (dosage, side effects, symptoms, interactions, pregnancy, driving),
   it is a complaint, it needs a real action (refund, change after payment, data deletion, account change),
   or the FAQ does not answer it. Then call create_jira_ticket. For medical questions also call notify_slack with #medical-ops.
   Possible medical emergencies get priority Highest.
4. Never give medical advice yourself.
5. Never promise times, deadlines or actions that are not in the FAQ (e.g. no "within 24 hours").
6. Use #medical-ops only for medical questions. Delivery or pharmacy problems go to #pharmacy-partners, everything else to #support.
7. Never put patient names or contact details in Slack messages, the ticket already has them.
Write tickets and replies in German. Always address the patient formally with "Sie", never "du"."""

RESULT_FORMAT = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": CATEGORIES},
        "needs_human": {"type": "boolean"},
        "reason": {"type": "string", "enum": ["medical", "no_faq", "action", "complaint", "none"]},
        "faq_ids": {"type": "array", "items": {"type": "string"}},
        "reply": {"type": "string"},
    },
    "required": ["category", "needs_human", "reason", "faq_ids", "reply"],
}

FINAL_INSTRUCTION = """Now give your final result as JSON.
category: the support category of the message.
needs_human: true if a human must take over (see the rules), else false.
reason: medical, no_faq, action, complaint or none if no human is needed.
faq_ids: the ids of the FAQ entries your reply is based on (empty if none fit).
reply: a short German reply to the patient in the formal "Sie" form (2 to 4 sentences) based only on the FAQ, ending with the source URL.
If a human takes over, the reply only says that the team will get back to them and gives no medical advice."""


def to_ollama_tools(mcp_tools):
    # ollama wants the openai style function format, mcp already gives us a json schema per tool
    tools = []
    for t in mcp_tools:
        tools.append({"type": "function", "function": {
            "name": t.name, "description": t.description, "parameters": t.inputSchema}})
    return tools


def short_result(name, result):
    # one readable line per tool result for the cli, the full result still goes to the model
    if isinstance(result, dict) and "error" in result:
        return "error: " + result["error"][:150]
    if name == "search_faq":
        hits = []
        for f in result:
            hits.append(f["id"] + " (" + str(f["score"]) + ")")
        return "found " + ", ".join(hits)
    if name == "get_order_status":
        if not result["found"]:
            return "order " + result["order_id"] + " not found"
        return result["order_id"] + ": " + result["status"] + ", " + result.get("detail", "")
    if name == "create_jira_ticket":
        return result["key"] + " created (" + result["backend"] + ")"
    if name == "notify_slack":
        return "posted to " + result["channel"] + " (" + result["backend"] + ")"
    return json.dumps(result, ensure_ascii=False)[:150]


async def handle_message(text, verbose=False):
    trace = []
    async with Client(mcp) as client:
        tools = to_ollama_tools(await client.list_tools())
        if verbose:
            print("\ntools from the mcp server:")
            for t in tools:
                params = ", ".join(t["function"]["parameters"]["properties"])
                print("  " + t["function"]["name"] + "(" + params + ")")
            print()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}]

        for step in range(MAX_STEPS):
            response = ollama.chat(model=MODEL, messages=messages, tools=tools, think=False,
                                   options={"temperature": 0})
            msg = response.message
            # print("step", step, msg.tool_calls, repr(msg.content[:200]))
            if not msg.tool_calls:
                break
            messages.append(msg)
            for call in msg.tool_calls:
                name = call.function.name
                args = call.function.arguments
                try:
                    result = (await client.call_tool(name, args)).data
                except Exception as e:
                    result = {"error": str(e)}  # give the error back so the model can fix its call
                trace.append({"tool": name, "args": args, "result": result})
                if verbose:
                    print("->", name, json.dumps(args, ensure_ascii=False))
                    print("   ", short_result(name, result))
                messages.append({"role": "tool", "content": json.dumps(result, ensure_ascii=False), "tool_name": name})

        # second call w/o tools so the model has to answer in the fixed json format
        messages.append({"role": "user", "content": FINAL_INSTRUCTION})
        final = ollama.chat(model=MODEL, messages=messages, format=RESULT_FORMAT, think=False,
                            options={"temperature": 0})
        result = json.loads(final.message.content)
        # print(final.message.content)

        # safety rule enforced in code too, the model alone is not trusted w/ this
        if result["category"] == "medizinisch":
            result["needs_human"] = True
            result["reason"] = "medical"

        # model sometimes decides a human is needed but never creates the ticket, so force it here
        made_ticket = False
        for call in trace:
            if call["tool"] == "create_jira_ticket" and "key" in str(call["result"]):
                made_ticket = True
        if result["needs_human"] and not made_ticket:
            priority = "Medium"
            if result["category"] == "medizinisch":
                priority = "High"
            args = {"summary": "Supportanfrage (" + result["reason"] + "): " + text[:80],
                    "description": text, "category": result["category"], "priority": priority,
                    "labels": ["auto_ticket"]}  # label so we can tell these apart from the model's tickets
            ticket = (await client.call_tool("create_jira_ticket", args)).data
            trace.append({"tool": "create_jira_ticket", "args": args, "result": ticket})
            if verbose:
                print("-> create_jira_ticket (auto)", json.dumps(args, ensure_ascii=False))
                print("   ", short_result("create_jira_ticket", ticket))

    result["tool_calls"] = trace
    return result


if __name__ == "__main__":
    # real jira/slack keys from .env, only here so the eval (imports handle_message) stays offline
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    message = input("user query: ") 
    out = asyncio.run(handle_message(message, verbose=True))
    print()
    print("category:   ", out["category"])
    print("needs_human:", out["needs_human"], "(" + out["reason"] + ")")
    print("faq:        ", ", ".join(out["faq_ids"]) or "-")
    tickets = []
    slack = []
    for call in out["tool_calls"]:
        if call["tool"] == "create_jira_ticket" and "key" in str(call["result"]):
            tickets.append(call["result"]["key"] + " " + call["args"]["summary"])
        if call["tool"] == "notify_slack" and "ok" in str(call["result"]):
            slack.append(call["args"]["channel"] + " " + call["args"]["text"])
    print("ticket:     ", " | ".join(tickets) or "-")
    print("slack:      ", " | ".join(slack) or "-")
    print("reply:      ", out["reply"])
