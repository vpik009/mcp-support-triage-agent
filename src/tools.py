
import json
from pathlib import Path

import numpy as np

from src.backends import get_jira_backend, get_slack_backend

DATA = Path(__file__).resolve().parent.parent / "data"

CATEGORIES = [
    "rezept_termin_dokumente", 
    "bestellung_lieferung", 
    "zahlung_rechnung", 
    "it_app",
    "datenschutz_recht_beschwerde", 
    "allgemein", 
    "medizinisch",
]
PRIORITIES = ["Lowest", "Low", "Medium", "High", "Highest"]  # jira default names
SLACK_CHANNELS = ["#support", "#medical-ops", "#pharmacy-partners"]  # just some placeholder channel names...

faq = json.loads((DATA / "faq.json").read_text(encoding="utf-8"))["faq"]
orders = json.loads((DATA / "mock_orders.json").read_text(encoding="utf-8"))["orders"]
# print(len(faq), "faq entries,", len(orders), "orders")


EMBED_MODEL = "intfloat/multilingual-e5-small"
VECTORS_FILE = DATA / "faq_vectors.npy"
encoder = None
faq_vectors = None


def build_faq_vectors():
    # e5 wants "passage: " in front of documents and "query: " in front of queries
    passages = []
    for f in faq:
        passages.append("passage: " + f["question"] + " " + f["answer"])
    vectors = get_encoder().encode(passages, normalize_embeddings=True)
    # print("faq vectors:", vectors.shape, vectors[0][:5])
    np.save(VECTORS_FILE, vectors)
    return vectors


def get_encoder():
    global encoder
    if encoder is None:
        from sentence_transformers import SentenceTransformer  # slow import, only load when needed
        encoder = SentenceTransformer(EMBED_MODEL, device="cpu")
    return encoder


def load_faq_vectors():
    global faq_vectors
    if faq_vectors is None:
        if VECTORS_FILE.exists():
            faq_vectors = np.load(VECTORS_FILE)
        else:
            faq_vectors = build_faq_vectors()
    return faq_vectors


def search_faq(query, top_k=2, min_score=None):
    q = get_encoder().encode(["query: " + query], normalize_embeddings=True)[0]
    scores = load_faq_vectors() @ q  # vectors are normalized so this is cosine similarity
    ranked = sorted(range(len(faq)), key=lambda i: scores[i], reverse=True)
    # print([(faq[i]["id"], round(float(scores[i]), 3)) for i in ranked[:5]])
    results = []
    for i in ranked[:top_k]:
        if min_score is not None and scores[i] < min_score:
            break
        f = faq[i]
        results.append({"id": f["id"], "question": f["question"], "answer": f["answer"],
                        "source_url": f["source_url"], "score": round(float(scores[i]), 3)})
    return results


def get_order_status(order_id):
    key = order_id.strip().upper()
    if key in orders:
        return {"found": True, "order_id": key, **orders[key]}
    # ppl often send the tracking number instead of the order number
    for oid, o in orders.items():
        if o.get("tracking") and o["tracking"].upper() == key:
            return {"found": True, "order_id": oid, **o}
    return {"found": False, "order_id": key, "detail": "Keine Bestellung mit dieser Nummer gefunden."}


def create_jira_ticket(summary, description, category, priority="Medium", labels=None):
    if category not in CATEGORIES:
        raise ValueError(f"unknown category {category!r}, expected one of {CATEGORIES}")
    if priority not in PRIORITIES:
        raise ValueError(f"unknown priority {priority!r}, expected one of {PRIORITIES}")
    all_labels = [category]
    if labels:
        all_labels += labels
    # same field names as the jira rest api so the backend can be swapped
    fields = {
        "project": "SUP",
        "issuetype": "Task",
        "summary": summary.strip()[:255],  # jira cuts summary at 255
        "description": description.strip(),
        "priority": priority,
        "labels": sorted(set(all_labels)),
    }
    # print("ticket:", fields)
    return get_jira_backend().create_ticket(fields)


def notify_slack(channel, text):
    if channel not in SLACK_CHANNELS:
        raise ValueError(f"unknown channel {channel!r}, expected one of {SLACK_CHANNELS}")
    return get_slack_backend().post_message(channel, text.strip())
