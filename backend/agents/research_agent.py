"""
Nexus AI - Research Agent
AI agent specialized in web research and information synthesis
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class ResearchAgent(BaseAgent):
    """
    Research Agent - Specialized in web research and information gathering.
    
    Capabilities:
    - Generate focused search queries
    - Search the web for information
    - Scrape and extract content from web pages
    - Synthesize findings into comprehensive summaries
    - Provide sources with citations
    """
    
    DEFAULT_ROLE = "Information gathering and research"
    
    SYSTEM_PROMPT = """You are a research assistant AI. Your job is to:
1. Gather accurate information from the web
2. Synthesize findings from multiple sources
3. Provide well-sourced summaries with citations
4. Be objective and present multiple perspectives when relevant

Always cite your sources. If information is uncertain, say so.
Format your responses clearly with sections and bullet points when appropriate."""

    def __init__(
        self,
        llm_manager=None,
        db_session=None,
        tools: List[Any] = None
    ):
        super().__init__(
            name="ResearchAgent",
            role=self.DEFAULT_ROLE,
            system_prompt=self.SYSTEM_PROMPT,
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools or []
        )
        
        self.max_search_results = 5
        self.max_scrape_pages = 3
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research task.
        
        Args:
            input_data: Must contain "query" or "original_prompt"
            
        Returns:
            Research results with summary and sources
        """
        self.start_execution()
        
        try:
            # Extract query
            query = input_data.get("query") or input_data.get("original_prompt", "")
            
            if not query:
                return self.format_output(None, status="error", error="No research query provided")
            
            self.log_action("research_started", {"query": query[:100]})
            
            # Run research workflow
            result = self._research_workflow(query)
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            self.log_action("research_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _research_workflow(self, query: str) -> Dict[str, Any]:
        """
        Main research workflow.
        
        Steps:
        1. Generate search queries
        2. Execute searches
        3. Scrape top sources
        4. Synthesize findings
        5. Format output
        """
        # Step 1: Generate search queries
        search_queries = self._generate_search_queries(query)
        self.log_action("queries_generated", {"queries": search_queries})
        
        # Step 2: Execute searches
        all_results = []
        for sq in search_queries:
            result = self.use_tool("web_search", query=sq, num_results=self.max_search_results)
            if result.get("success") and result.get("data"):
                all_results.extend(result["data"])
        
        # Deduplicate results
        unique_results = self._deduplicate_results(all_results)
        self.log_action("search_completed", {"total_results": len(unique_results)})
        
        if not unique_results:
            # No search results - use LLM knowledge only
            return self._synthesize_without_sources(query)
        
        # Step 3: Rank and scrape top sources
        ranked_urls = self._rank_sources(unique_results)
        scraped_content = []
        
        for url_info in ranked_urls[:self.max_scrape_pages]:
            url = url_info.get("url", "")
            if not url:
                continue
                
            result = self.use_tool("web_scraper", url=url, extract_type="text")
            if result.get("success") and result.get("data"):
                scraped_content.append({
                    "url": url,
                    "title": url_info.get("title", ""),
                    "content": result["data"][:3000]  # Limit content size
                })
        
        self.log_action("scraping_completed", {"pages_scraped": len(scraped_content)})
        
        # Step 4: Synthesize findings
        synthesis = self._synthesize_findings(query, scraped_content, unique_results)
        
        # Step 5: Calculate confidence and format
        confidence = self._calculate_confidence(unique_results, scraped_content)
        
        return {
            "summary": synthesis.get("summary", ""),
            "key_findings": synthesis.get("key_findings", []),
            "sources": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("snippet", "")[:150]
                }
                for r in unique_results[:5]
            ],
            "confidence_score": confidence,
            "query": query,
            "researched_at": datetime.utcnow().isoformat()
        }
    
    def _generate_search_queries(self, query: str) -> List[str]:
        """
        Generate focused search queries from user query.
        """
        prompt = f"""Break this research query into 2-3 specific search queries that will help find comprehensive information:

Query: {query}

Return ONLY a JSON array of search queries, nothing else. Example:
["search query 1", "search query 2", "search query 3"]"""

        response = self.generate_response(prompt)
        
        if response:
            try:
                # Try to parse JSON
                # Handle markdown code blocks
                if "```" in response:
                    response = response.split("```")[1]
                    if response.startswith("json"):
                        response = response[4:]
                
                queries = json.loads(response.strip())
                if isinstance(queries, list) and len(queries) > 0:
                    return queries[:3]
            except:
                pass
        
        # Fallback: use original query
        return [query]
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs from results."""
        seen_urls = set()
        unique = []
        
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(r)
        
        return unique
    
    def _rank_sources(self, results: List[Dict]) -> List[Dict]:
        """
        Rank sources by quality/relevance.
        
        Prioritizes authoritative domains.
        """
        def score(r):
            url = r.get("url", "").lower()
            score = 0
            
            # Prioritize authoritative domains
            if ".edu" in url:
                score += 10
            if ".gov" in url:
                score += 10
            if "wikipedia" in url:
                score += 5
            if "github" in url:
                score += 3
            
            # Deprioritize social media
            if any(s in url for s in ["twitter.com", "facebook.com", "reddit.com", "tiktok"]):
                score -= 5
            
            # Prefer results with snippets
            if r.get("snippet"):
                score += 2
            
            return score
        
        return sorted(results, key=score, reverse=True)
    
    def _synthesize_findings(
        self, 
        query: str, 
        scraped_content: List[Dict],
        search_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Synthesize findings from scraped content.
        """
        # Build context from scraped content
        context_parts = []
        for sc in scraped_content:
            context_parts.append(f"Source: {sc['title']} ({sc['url']})\n{sc['content'][:1500]}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        # If no scraped content, use search snippets
        if not context:
            context = "\n".join([
                f"- {r.get('title', '')}: {r.get('snippet', '')}"
                for r in search_results[:5]
            ])
        
        prompt = f"""Based on the following information, provide a comprehensive answer to the research query.

RESEARCH QUERY: {query}

SOURCES:
{context}

Provide your response in this exact JSON format:
{{
    "summary": "A comprehensive 2-3 paragraph summary answering the query",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3", "Finding 4", "Finding 5"]
}}

Be accurate and cite information from the sources. If sources are insufficient, acknowledge limitations."""

        response = self.generate_response(prompt, use_cache=False)
        
        if response:
            try:
                # Parse JSON response
                if "```" in response:
                    response = response.split("```")[1]
                    if response.startswith("json"):
                        response = response[4:]
                
                return json.loads(response.strip())
            except:
                # If JSON parsing fails, return raw response
                return {
                    "summary": response,
                    "key_findings": []
                }
        
        return {
            "summary": "Unable to synthesize research findings.",
            "key_findings": []
        }
    
    def _synthesize_without_sources(self, query: str) -> Dict[str, Any]:
        """
        Fallback when no web sources are available.
        """
        prompt = f"""Answer this research query based on your knowledge:

Query: {query}

Provide your response in this exact JSON format:
{{
    "summary": "A comprehensive answer based on general knowledge",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"]
}}

Note: This response is based on training data, not live web search."""

        response = self.generate_response(prompt, use_cache=False)
        
        result = {
            "summary": "Research completed using AI knowledge (no web sources found).",
            "key_findings": [],
            "sources": [],
            "confidence_score": 0.3,  # Lower confidence without sources
            "query": query,
            "researched_at": datetime.utcnow().isoformat(),
            "note": "No web sources found. Response based on AI knowledge."
        }
        
        if response:
            try:
                if "```" in response:
                    response = response.split("```")[1]
                    if response.startswith("json"):
                        response = response[4:]
                
                parsed = json.loads(response.strip())
                result["summary"] = parsed.get("summary", result["summary"])
                result["key_findings"] = parsed.get("key_findings", [])
            except:
                result["summary"] = response
        
        return result
    
    def _calculate_confidence(
        self, 
        search_results: List[Dict],
        scraped_content: List[Dict]
    ) -> float:
        """
        Calculate confidence score based on research quality.
        """
        score = 0.0
        
        # Number of sources found
        if len(search_results) >= 5:
            score += 0.3
        elif len(search_results) >= 2:
            score += 0.2
        elif len(search_results) >= 1:
            score += 0.1
        
        # Successful scrapes
        if len(scraped_content) >= 3:
            score += 0.3
        elif len(scraped_content) >= 1:
            score += 0.2
        
        # Quality of sources
        authoritative = sum(
            1 for r in search_results 
            if any(d in r.get("url", "") for d in [".edu", ".gov", "wikipedia"])
        )
        if authoritative >= 2:
            score += 0.2
        elif authoritative >= 1:
            score += 0.1
        
        # Content length
        total_content = sum(len(sc.get("content", "")) for sc in scraped_content)
        if total_content >= 5000:
            score += 0.2
        elif total_content >= 1000:
            score += 0.1
        
        return min(round(score, 2), 1.0)
