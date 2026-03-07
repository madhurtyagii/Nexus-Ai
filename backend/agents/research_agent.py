"""Nexus AI - Research Agent.

This module implements the ResearchAgent, which is specialized in gathering 
information from the web, scraping content, and synthesizing findings into 
comprehensive reports with citations.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class ResearchAgent(BaseAgent):
    """Agent specialized in web research and information gathering.
    
    The ResearchAgent can generate optimized search queries, retrieve 
    information from multiple search engines, scrape web pages for 
    detailed content, and synthesize results into a cohesive summary 
    with proper citations.
    
    Attributes:
        name: Agent identifier ("ResearchAgent").
        role: Description of the agent's purpose.
        system_prompt: Core instructions for LLM interactions.
        max_search_results: Number of results to fetch per query.
        max_scrape_pages: Limit on the number of full pages to scrape.
        
    Example:
        >>> agent = ResearchAgent(llm_manager, db_session)
        >>> result = agent.execute({"query": "Recent advances in fusion energy"})
        >>> print(result["output"]["summary"])
    """
    
    DEFAULT_ROLE = "Information gathering and research"
    
    SYSTEM_PROMPT = """You are a highly capable and talkative research assistant. Your goal is to gather accurate information and present it in a friendly, conversational manner.
    
    Your job is to:
    1. **Deep Research**: Gather comprehensive and accurate info from the web.
    2. **Friendly Synthesis**: Summarize findings in a way that is easy to read and understand.
    3. **Proper Citations**: Always list your sources clearly so the user can verify.
    4. **Objective Insights**: Present multiple perspectives and be honest about uncertainties.
    
    Always:
    - Be talkative and engaging. Start with a friendly intro like "I've looked into this for you..."
    - Use bullet points and clear sections for readability.
    - If a user asks a simple question, give a direct, friendly answer first, then provide the research depth.
    
    Respond as a helpful research partner, not a dry search engine."""

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
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"DEBUG: ResearchAgent.execute called with: {input_data}")
        self.start_execution()
        
        try:
            # Extract query
            query = (
                input_data.get("query") or 
                input_data.get("prompt") or 
                input_data.get("task") or 
                input_data.get("user_prompt", "")
            )
            
            if not query:
                return self.format_output(None, status="error", error="No research query provided")

            max_depth = input_data.get("max_depth", 2) # Default 2 loops for efficiency
            current_depth = 0
            research_history = []
            
            print(f"🔍 ResearchAgent: Starting recursive research for '{query}' (Max Depth: {max_depth})")
            
            # Initial Research Phase
            current_results = await self._research_workflow(query)
            research_history.append(current_results)
            
            # Recursive "Digging" Phase
            while current_depth < max_depth:
                confidence = current_results.get("confidence_score", 0.0)
                
                # If we have high confidence, we might be done
                if confidence > 0.85:
                    break
                
                current_depth += 1
                self.log_action("research_loop", {"depth": current_depth, "confidence": confidence})
                
                # Identify what's missing or needs more detail
                follow_up_query = self._identify_research_gaps(query, current_results)
                if not follow_up_query:
                    break
                    
                print(f"🔄 ResearchAgent: Loop {current_depth} - Investigating gaps: '{follow_up_query}'")
                current_results = await self._research_workflow(follow_up_query)
                research_history.append(current_results)

            # Final Step: Synthesize all loops into a "Research Paper"
            final_report = self._synthesize_final_report(query, research_history)
            
            self.end_execution()
            return self.format_output(final_report)
            
        except Exception as e:
            self.log_action("research_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))

    def _identify_research_gaps(self, original_query: str, last_results: Dict[str, Any]) -> Optional[str]:
        """Ask LLM to find missing info and generate a follow-up query."""
        summary = last_results.get("summary", "")
        
        prompt = f"""You are a research analyst. Review the following research summary and identify any missing information, technical depth gaps, or unanswered questions relative to the original query.
        
ORIGINAL QUERY: {original_query}
CURRENT SUMMARY: {summary}

If there are significant gaps, provide ONE targeted follow-up search query to fill those gaps. 
If the summary is already comprehensive, respond with 'DONE'.

Response (Query or 'DONE'):"""

        response = self.generate_response(prompt, use_cache=False)
        if response and "DONE" not in response.upper():
            return response.strip().strip('"').strip("'")
        return None

    def _synthesize_final_report(self, original_query: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine all research phases into a final high-quality report."""
        all_key_findings = []
        all_sources = []
        full_context = ""

        for i, h in enumerate(history):
            all_key_findings.extend(h.get("key_findings", []))
            all_sources.extend(h.get("sources", []))
            full_context += f"\n--- Research Phase {i+1} ---\n{h.get('summary', '')}\n"

        prompt = f"""You are a Senior Research Analyst. Synthesize the following multi-phase research into a final professional report.

TOPIC: {original_query}

DATA FROM MULTIPLE PHASES:
{full_context}

Respond ONLY with valid JSON in this exact format (no markdown fences, no extra text):
{{
    "title": "A professional title for the research paper",
    "summary": "A deep, multi-paragraph executive summary",
    "sections": [
        {{"heading": "Section Heading", "content": "Detailed analysis..."}}
    ],
    "conclusion": "Final wrap-up and insights",
    "all_key_findings": ["Finding 1", "Finding 2"]
}}"""

        response = self.generate_response(prompt, use_cache=False)
        
        try:
            import re as _re
            json_str = (response or "").strip()
            
            # Strip markdown code fences if present
            if "```" in json_str:
                json_str = _re.sub(r"```(?:json)?\s*", "", json_str).replace("```", "").strip()
            
            # Extract the outermost JSON object (handles extra text before/after)
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start != -1 and end > start:
                json_str = json_str[start:end]
            
            final_paper = json.loads(json_str)
            final_paper["sources"] = self._deduplicate_results(all_sources)[:10]
            final_paper["confidence_score"] = max((h.get("confidence_score", 0) for h in history), default=0)
            return final_paper

        except Exception:
            # Robust fallback: build a structured result from what we have
            summary_parts = []
            for h in history:
                s = h.get("summary", "")
                if s:
                    summary_parts.append(s)

            return {
                "title": f"Research Report: {original_query}",
                "summary": "\n\n".join(summary_parts) or "Research completed.",
                "sections": [],
                "all_key_findings": list(dict.fromkeys(all_key_findings))[:15],  # deduplicated
                "conclusion": "",
                "sources": self._deduplicate_results(all_sources)[:10],
                "confidence_score": 0.5
            }
    
    async def _research_workflow(self, query: str) -> Dict[str, Any]:
        """Coordinates the sequential steps of the research process.
        
        Args:
            query: The refined search query to process.
            
        Returns:
            dict: Structured research data synthesized from multiple sources.
        """
        # Step 1: Generate search queries
        search_queries = self._generate_search_queries(query)
        self.log_action("queries_generated", {"queries": search_queries})
        
        # Step 2: Execute searches
        all_results = []
        for sq in search_queries:
            result = await self.use_tool("web_search", query=sq, num_results=self.max_search_results)
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
                
            result = await self.use_tool("web_scraper", url=url, extract_type="text")
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
                clean_response = response.strip()
                if "```" in clean_response:
                    # Extract from markdown code block
                    parts = clean_response.split("```")
                    if len(parts) >= 2:
                        clean_response = parts[1]
                        if clean_response.startswith("json"):
                            clean_response = clean_response[4:]
                
                clean_response = clean_response.strip()
                parsed = json.loads(clean_response)
                return parsed
            except Exception as e:
                # If JSON parsing fails, try to extract summary using regex
                import re
                
                # Try to find summary content
                summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)', response, re.DOTALL)
                if summary_match:
                    summary_text = summary_match.group(1)
                    # Unescape common JSON escapes
                    summary_text = summary_text.replace('\\n', ' ').replace('\\"', '"').replace('\\/', '/')
                    
                    # Try to find key_findings
                    findings = []
                    findings_match = re.findall(r'"([^"]+)"(?=\s*[,\]])', response)
                    # Filter to get only finding-like strings (longer than 20 chars)
                    findings = [f for f in findings_match if len(f) > 20 and 'summary' not in f.lower()][:5]
                    
                    return {
                        "summary": summary_text,
                        "key_findings": findings
                    }
                
                # Final fallback: return raw response cleaned up
                return {
                    "summary": response.replace('{', '').replace('}', '').replace('"', '').strip()[:1000],
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
