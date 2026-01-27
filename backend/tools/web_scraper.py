"""
Nexus AI - Web Scraper Tool
Extract content from web pages
"""

import time
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import httpx

from tools.base_tool import BaseTool


class WebScraperTool(BaseTool):
    """
    Web scraping tool to extract content from web pages.
    
    Supports extracting text, links, and images.
    """
    
    def __init__(self, timeout: float = 10.0):
        super().__init__(
            name="web_scraper",
            description="Extract content from web pages",
            parameters={
                "url": "URL to scrape (required)",
                "extract_type": "Type of content: text, links, images, all (optional, default: text)"
            }
        )
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    
    def execute(
        self, 
        url: str, 
        extract_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Execute web scraping.
        
        Args:
            url: URL to scrape
            extract_type: Type of extraction (text, links, images, all)
            
        Returns:
            Scraped content dictionary
        """
        # Validate URL
        if not url or not url.strip():
            return {"success": False, "error": "URL cannot be empty", "data": None}
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        start_time = time.time()
        
        try:
            # Fetch page
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, headers=self.headers)
                
                if response.status_code >= 400:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.reason_phrase}",
                        "data": None,
                        "url": url
                    }
                
                html = response.text
            
            # Extract content based on type
            if extract_type == "text":
                data = self._extract_text(html)
            elif extract_type == "links":
                data = self._extract_links(html, url)
            elif extract_type == "images":
                data = self._extract_images(html, url)
            elif extract_type == "all":
                data = {
                    "text": self._extract_text(html),
                    "links": self._extract_links(html, url),
                    "images": self._extract_images(html, url)
                }
            else:
                data = self._extract_text(html)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "data": data,
                "url": url,
                "content_length": len(str(data)),
                "execution_time_ms": execution_time
            }
            
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out",
                "data": None,
                "url": url
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Failed to connect to URL",
                "data": None,
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "url": url
            }
    
    def _extract_text(self, html: str) -> str:
        """
        Extract clean text from HTML.
        """
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<noscript[^>]*>.*?</noscript>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Try to extract main content
        main_content = self._extract_main_content(html)
        if main_content:
            html = main_content
        
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Decode HTML entities
        text = self._decode_html_entities(text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Truncate if too long
        if len(text) > 10000:
            text = text[:10000] + "..."
        
        return text
    
    def _extract_main_content(self, html: str) -> Optional[str]:
        """
        Try to extract main content area.
        """
        # Look for article or main tags
        patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*id="content"[^>]*>(.*?)</div>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_links(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """
        Extract all links from HTML.
        """
        links = []
        seen = set()
        
        # Find all href attributes
        pattern = r'<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for href, text in matches:
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Skip duplicates and anchors
            if absolute_url in seen or href.startswith('#'):
                continue
            seen.add(absolute_url)
            
            links.append({
                "url": absolute_url,
                "text": text.strip()[:100]
            })
        
        return links[:50]  # Limit to 50 links
    
    def _extract_images(self, html: str, base_url: str) -> List[Dict[str, str]]:
        """
        Extract all images from HTML.
        """
        images = []
        seen = set()
        
        # Find all img src attributes
        pattern = r'<img[^>]*src="([^"]+)"[^>]*>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for src in matches:
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, src)
            
            if absolute_url in seen:
                continue
            seen.add(absolute_url)
            
            # Extract alt text
            alt_pattern = rf'<img[^>]*src="{re.escape(src)}"[^>]*alt="([^"]*)"'
            alt_match = re.search(alt_pattern, html, re.IGNORECASE)
            alt = alt_match.group(1) if alt_match else ""
            
            images.append({
                "url": absolute_url,
                "alt": alt[:100]
            })
        
        return images[:30]  # Limit to 30 images
    
    def _decode_html_entities(self, text: str) -> str:
        """
        Decode common HTML entities.
        """
        entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'",
            '&mdash;': '—',
            '&ndash;': '–',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
        }
        
        for entity, char in entities.items():
            text = text.replace(entity, char)
        
        # Handle numeric entities
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
        
        return text
