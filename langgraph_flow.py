# langgraph_flow.py

from typing import TypedDict
import json

from langgraph.graph import StateGraph, END

from personas import PERSONAS
from mock_tools import mock_searxng_search


class ContentState(TypedDict):
    bot_id: str
    persona: str
    topic: str
    search_query: str
    search_results: str
    post_content: str
    final_json: str


def decide_search_node(state: ContentState):
    """
    Decide what topic the bot wants to post about today
    based on its persona.
    """
    persona = state["persona"].lower()

    if "crypto" in persona or "space exploration" in persona or "technology" in persona:
        state["topic"] = "AI and technology"
        state["search_query"] = "OpenAI AI latest news"

    elif "privacy" in persona or "social media" in persona or "tech monopolies" in persona:
        state["topic"] = "Privacy and social media"
        state["search_query"] = "privacy social media latest news"

    elif "markets" in persona or "interest rates" in persona or "roi" in persona:
        state["topic"] = "Markets and interest rates"
        state["search_query"] = "markets interest rates latest news"

    else:
        state["topic"] = "General technology"
        state["search_query"] = "technology latest news"

    return state


def web_search_node(state: ContentState):
    """
    Call the mock search tool to get recent context.
    """
    result = mock_searxng_search.invoke(state["search_query"])
    state["search_results"] = result
    return state


def draft_post_node(state: ContentState):
    """
    Draft a strongly opinionated short post
    using persona + context.
    """
    persona = state["persona"].lower()
    topic = state["topic"]
    context = state["search_results"]

    if "crypto" in persona or "technology" in persona:
        post = (
            f"AI keeps proving the pessimists wrong. {context} "
            f"This is exactly why betting on innovation always wins."
        )

    elif "privacy" in persona or "tech monopolies" in persona:
        post = (
            f"{context} Another reminder that Big Tech keeps expanding power "
            f"while people keep cheering for their own surveillance."
        )

    elif "markets" in persona or "roi" in persona:
        post = (
            f"{context} If you are not tracking the ROI implications of this trend, "
            f"you are already behind the market."
        )

    else:
        post = f"{context} This trend is shaping the next phase of digital systems."

    # Keep it close to 280 chars
    state["post_content"] = post[:280]
    return state


def format_json_node(state: ContentState):
    """
    Produce strict JSON output.
    """
    output = {
        "bot_id": state["bot_id"],
        "topic": state["topic"],
        "post_content": state["post_content"]
    }

    state["final_json"] = json.dumps(output, indent=2)
    return state


def build_content_graph():
    """
    Build the LangGraph workflow.
    """
    graph = StateGraph(ContentState)

    graph.add_node("decide_search", decide_search_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("draft_post", draft_post_node)
    graph.add_node("format_json", format_json_node)

    graph.set_entry_point("decide_search")

    graph.add_edge("decide_search", "web_search")
    graph.add_edge("web_search", "draft_post")
    graph.add_edge("draft_post", "format_json")
    graph.add_edge("format_json", END)

    return graph.compile()


if __name__ == "__main__":
    graph = build_content_graph()

    sample_state = {
        "bot_id": "bot_a",
        "persona": PERSONAS["bot_a"]["description"],
        "topic": "",
        "search_query": "",
        "search_results": "",
        "post_content": "",
        "final_json": ""
    }

    result = graph.invoke(sample_state)

    print("Generated JSON Output:\n")
    print(result["final_json"])