"""
Tools Module: Real-World Web Search via Tavily API and Encyclopedic Lookup via Wikipedia.
Directly compatible with Google Gemini function calling.
"""

import json
import os
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from citation import CitationManager

USER_AGENT = "ResearchAgent/2.0 (Mozilla/5.0; Windows NT 10.0; Win64; x64)"
DEFAULT_TIMEOUT = 10


class ResearchTools:
    """Provides tools for live Tavily web search and Wikipedia lookup with automatic citation tracking."""

    def __init__(self, citation_manager: CitationManager, tavily_api_key: Optional[str] = None):
        self.citation_manager = citation_manager
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

    def tavily_search(self, query: str, max_results: int = 5) -> str:
        """Searches the live web via Tavily to retrieve authoritative real-world articles, documentation,

        benchmarks, and current news with full source URLs for citation.

        Args:
            query: The research search query (e.g., "DeepSeek R1 architecture reinforcement learning").
            max_results: Number of top results to return (default: 5, max: 8).

        Returns:
            JSON string containing retrieved web sources, citation IDs, titles, URLs, and snippets.
        """
        clean_query = query.strip()
        if not clean_query:
            return json.dumps({"status": "error", "message": "Search query cannot be empty."})

        if not self.tavily_api_key:
            return json.dumps({
                "status": "error",
                "error_type": "MissingAPIKey",
                "message": "TAVILY_API_KEY is not configured.",
                "guidance": "Please set TAVILY_API_KEY in your .env file or fallback to search_wikipedia."
            })

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            response = client.search(
                query=clean_query,
                max_results=min(max(1, max_results), 8),
                search_depth="basic"
            )

            results = response.get("results", [])
            if not results:
                return json.dumps({
                    "status": "warning",
                    "message": f"No web search results found for: '{clean_query}'.",
                    "guidance": "Try alternative keywords or use search_wikipedia."
                })

            formatted_results = []
            for item in results:
                title = item.get("title", "Untitled Web Source")
                url = item.get("url", "")
                content = item.get("content", "")
                if not url:
                    continue

                citation = self.citation_manager.register(
                    title=title,
                    url=url,
                    snippet=content,
                    tool_origin="tavily_search"
                )
                formatted_results.append({
                    "citation_id": citation.id,
                    "title": citation.title,
                    "url": citation.url,
                    "snippet": citation.snippet
                })

            return json.dumps({
                "status": "success",
                "query": clean_query,
                "count": len(formatted_results),
                "sources": formatted_results
            }, indent=2)

        except requests.exceptions.Timeout:
            return json.dumps({"status": "error", "message": "Tavily search request timed out."})
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error_type": type(e).__name__,
                "message": f"Tavily search failed: {str(e)}",
                "guidance": "Check your TAVILY_API_KEY or use search_wikipedia instead."
            })

    def search_wikipedia(self, topic: str, max_results: int = 2) -> str:
        """Searches English Wikipedia for encyclopedic overviews, historical context, scientific concepts,

        and foundational background knowledge.

        Args:
            topic: The entity or concept to search on Wikipedia (e.g., "Transformer machine learning").
            max_results: Maximum number of article summaries to fetch (default: 2).

        Returns:
            JSON string containing Wikipedia article summaries with canonical URLs and citation IDs.
        """
        clean_topic = topic.strip()
        if not clean_topic:
            return json.dumps({"status": "error", "message": "Topic cannot be empty."})

        try:
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": clean_topic,
                "format": "json",
                "srlimit": min(max(1, max_results), 4),
                "utf8": 1
            }
            headers = {"User-Agent": USER_AGENT}
            resp = requests.get(search_url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            search_hits = resp.json().get("query", {}).get("search", [])

            if not search_hits:
                return json.dumps({
                    "status": "warning",
                    "message": f"No Wikipedia articles found for '{clean_topic}'.",
                    "guidance": "Try different phrasing or use tavily_search for broad web results."
                })

            summaries = []
            for hit in search_hits[:max_results]:
                title = hit.get("title")
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
                try:
                    s_resp = requests.get(summary_url, headers=headers, timeout=DEFAULT_TIMEOUT)
                    if s_resp.status_code == 200:
                        s_data = s_resp.json()
                        extract = s_data.get("extract", "")
                        page_url = s_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{title}")
                    else:
                        extract = BeautifulSoup(hit.get("snippet", ""), "html.parser").get_text()
                        page_url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(title)}"
                except Exception:
                    extract = BeautifulSoup(hit.get("snippet", ""), "html.parser").get_text()
                    page_url = f"https://en.wikipedia.org/wiki/{requests.utils.quote(title)}"

                citation = self.citation_manager.register(
                    title=f"Wikipedia: {title}",
                    url=page_url,
                    snippet=extract,
                    tool_origin="search_wikipedia"
                )
                summaries.append({
                    "citation_id": citation.id,
                    "title": citation.title,
                    "url": citation.url,
                    "summary": extract[:1000]
                })

            return json.dumps({
                "status": "success",
                "topic": clean_topic,
                "count": len(summaries),
                "articles": summaries
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "error_type": type(e).__name__,
                "message": f"Wikipedia query failed: {str(e)}",
                "guidance": "Try tavily_search instead."
            })
