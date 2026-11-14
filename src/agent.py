# local agent: reads a support message, uses the mcp tools through qwen3 on ollama, returns a structured result
# run: uv run python -m src.agent "Mein Paket BW-2026-49120 bewegt sich seit 9 Tagen nicht."
import asyncio
import json
import sys

import ollama
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


async def handle_message(text, verbose=False):
    trace = []
    async with Client(mcp) as client:
        tools = to_ollama_tools(await client.list_tools())
        print("\n\ntools:", tools)
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
                    print("   ", json.dumps(result, ensure_ascii=False)[:300])
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
    result["tool_calls"] = trace
    return result


if __name__ == "__main__":
    message = input("user query: ") 
    out = asyncio.run(handle_message(message, verbose=True))
    print()
    print("category:   ", out["category"])
    print("needs_human:", out["needs_human"], "(" + out["reason"] + ")")
    print("faq:        ", ", ".join(out["faq_ids"]) or "-")
    print("reply:      ", out["reply"])
