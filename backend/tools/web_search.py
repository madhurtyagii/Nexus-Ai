"""
Nexus AI - Web Search Tool
Search the web using Tavily API (optimized for AI agents)
Falls back to DuckDuckGo if Tavily unavailable
"""

import os
import time
from typing import Dict, Any, List
import httpx

from tools.base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    Web search tool using Tavily API (primary) with DuckDuckGo fallback.
    
    Tavily is specifically designed for AI agents and provides
    high-quality, relevant search results.
    """
    
    TAVILY_API_URL = "https://api.tavily.com/search"
    DUCKDUCKGO_API = "https://api.duckduckgo.com/"
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="web_search",
            description="Search the web for information using Tavily AI",
            parameters={
                "query": "Search query string (required)",
                "num_results": "Number of results to return (optional, default 5)"
            }
        )
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")
        self.timeout = 15.0
        
        if self.api_key:
            print(f"✅ WebSearchTool initialized with Tavily API")
        else:
            print(f"⚠️ WebSearchTool using DuckDuckGo fallback (no Tavily API key)")
    
    def execute(
        self, 
        query: str, 
        num_results: int = 5
    ) -> Dict[str, Any]:
        """
        Execute web search.
        
        Args:
            query: Search query
            num_results: Max results to return
            
        Returns:
            Search results dictionary
        """
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Search query cannot be empty",
                "data": []
            }
        
        start_time = time.time()
        
        # Try Tavily first if API key available
        if self.api_key:
            result = self._search_tavily(query, num_results)
            if result.get("success"):
                result["execution_time_ms"] = int((time.time() - start_time) * 1000)
                return result
        
        # Fallback to DuckDuckGo
        result = self._search_duckduckgo(query, num_results)
        result["execution_time_ms"] = int((time.time() - start_time) * 1000)
        return result
    
    def _search_tavily(
        self, 
        query: str, 
        num_results: int
    ) -> Dict[str, Any]:
        """
        Search using Tavily API.
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.TAVILY_API_URL,
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": True,
                        "include_raw_content": False,
                        "max_results": num_results
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    results = []
                    
                    # Add the AI-generated answer if available
                    if data.get("answer"):
                        results.append({
                            "title": "AI Summary",
                            "url": "",
                            "snippet": data["answer"],
                            "source": "Tavily AI",
                            "score": 1.0
                        })
                    
                    # Add search results
                    for r in data.get("results", []):
                        results.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "snippet": r.get("content", "")[:500],
                            "source": "Tavily",
                            "score": r.get("score", 0)
                        })
                    
                    return {
                        "success": True,
                        "data": results[:num_results],
                        "query": query,
                        "total_results": len(results),
                        "provider": "tavily"
                    }
                else:
                    print(f"⚠️ Tavily API error: {response.status_code}")
                    return {"success": False, "error": f"Tavily API error: {response.status_code}"}
                    
        except Exception as e:
            print(f"⚠️ Tavily search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _search_duckduckgo(
        self, 
        query: str, 
        num_results: int
    ) -> Dict[str, Any]:
        """
        Fallback search using DuckDuckGo.
        """
        results = []
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                # DuckDuckGo Instant Answer API
                response = client.get(
                    self.DUCKDUCKGO_API,
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract abstract result
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("Heading", "Result"),
                            "url": data.get("AbstractURL", ""),
                            "snippet": data.get("Abstract", "")[:500],
                            "source": data.get("AbstractSource", "DuckDuckGo")
                        })
                    
                    # Extract related topics
                    for topic in data.get("RelatedTopics", [])[:num_results-1]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": topic.get("Text", "")[:100],
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", "")[:500],
                                "source": "DuckDuckGo"
                            })
            
            # Try HTML scraping if not enough results
            if len(results) < num_results:
                html_results = self._scrape_duckduckgo_html(query, num_results - len(results))
                results.extend(html_results)
            
            return {
                "success": True,
                "data": results[:num_results],
                "query": query,
                "total_results": len(results),
                "provider": "duckduckgo"
            }
            
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "query": query
            }
    
    def _scrape_duckduckgo_html(
        self, 
        query: str, 
        num_results: int
    ) -> List[Dict[str, Any]]:
        """
        Fallback: Scrape DuckDuckGo HTML results.
        """
        results = []
        
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code == 200:
                    html = response.text
                    
                    import re
                    
                    # Extract URLs and titles
                    link_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
                    snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
                    
                    links = re.findall(link_pattern, html)
                    snippets = re.findall(snippet_pattern, html)
                    
                    for i, (url, title) in enumerate(links[:num_results]):
                        snippet = snippets[i] if i < len(snippets) else ""
                        results.append({
                            "title": title.strip(),
                            "url": url,
                            "snippet": snippet.strip()[:500],
                            "source": "DuckDuckGo"
                        })
                        
        except Exception as e:
            print(f"⚠️ HTML scrape error: {e}")
        
        return results
