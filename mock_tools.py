from langchain.tools import tool


@tool
def mock_searxng_search(query: str) -> str:
    """
    Return hardcoded news headlines based on keywords in the query.
    """
    query = query.lower()

    if "crypto" in query:
        return "Bitcoin hits new all-time high amid regulatory ETF approvals."

    if "ai" in query or "openai" in query:
        return "OpenAI releases a new model, intensifying debate about job automation."

    if "markets" in query or "interest rates" in query:
        return "Markets rally as investors anticipate interest rate cuts."

    if "privacy" in query or "social media" in query:
        return "Privacy advocates criticize major social platforms over data collection."

    if "space" in query or "elon" in query:
        return "SpaceX announces another ambitious launch schedule this quarter."

    return "No major headline found, but online debate continues around the topic."