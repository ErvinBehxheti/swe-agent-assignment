from duckduckgo_search import DDGS

from src.config import MAX_SEARCH_RESULTS


def web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> dict:
    """
    Search the web using DuckDuckGo and return a list of results.

    Each result contains a title, URL, and short snippet.
    Returns a dict with 'results' on success or 'error' on failure.
    No API key is required — DuckDuckGo is used directly.
    """
    if not query or not query.strip():
        return {"error": "Search query cannot be empty"}

    try:
        with DDGS() as ddgs:
            hits = list(ddgs.text(query.strip(), max_results=max_results))

        if not hits:
            return {"results": [], "query": query, "message": "No results found"}

        results = [
            {
                "title": hit.get("title", ""),
                "url": hit.get("href", ""),
                "snippet": hit.get("body", ""),
            }
            for hit in hits
        ]
        return {"results": results, "query": query}

    except Exception as exc:
        return {"error": f"Search failed: {exc}", "query": query}
