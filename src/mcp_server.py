# mcp server that gives the support tools to the agent

from fastmcp import FastMCP

from src import tools

mcp = FastMCP("bloomwell-support-tools")


@mcp.tool
def search_faq(query: str) -> list[dict]:
    """Search the public Bloomwell FAQ. Use this before drafting any answer to a patient.
    Returns the best matching entries with question, answer and source URL. Base the reply only
    on these answers; if nothing fits, the message needs a human."""
    return tools.search_faq(query, top_k=2)  # fixed, the model kept asking for only 1


@mcp.tool
def get_order_status(order_id: str) -> dict:
    """Look up the status of an order by order number (e.g. BW-2026-48213) or DHL tracking number.
    Use it when the message mentions an order or tracking number."""
    return tools.get_order_status(order_id)


@mcp.tool
def create_jira_ticket(summary: str, description: str, category: str, priority: str = "Medium",
                       labels: list[str] | None = None) -> dict:
    """Create a ticket for the support team when a human has to act: medical questions, complaints,
    requests that need a real action (refund, address change after payment, data deletion) or
    questions the FAQ does not answer. Do NOT create tickets for questions the FAQ fully answers.
    category: one of rezept_termin_dokumente, bestellung_lieferung, zahlung_rechnung, it_app,
    datenschutz_recht_beschwerde, allgemein, medizinisch.
    priority: Lowest, Low, Medium, High or Highest. Use Highest for possible medical emergencies,
    High for other medical questions. Write summary and description in German."""
    return tools.create_jira_ticket(summary, description, category, priority, labels)


@mcp.tool
def notify_slack(channel: str, text: str) -> dict:
    """Send a short notice to a team channel: #medical-ops for medical questions,
    #pharmacy-partners for problems a pharmacy must solve, #support for everything else.
    Only use it together with a ticket, and only for medical or urgent cases."""
    return tools.notify_slack(channel, text)


if __name__ == "__main__":
    mcp.run()
