"""
Web Search integration for Skynet Core
Provides real-time web search capabilities with Azure Search and DuckDuckGo support
"""

import httpx
import json
import re
import os
from urllib.parse import quote_plus, urljoin
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import asyncio


class AzureSearchTool:
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        # API key and endpoint can be provided directly or via env vars
        self.api_key = api_key
        # Prefer endpoint from environment; do not hardcode provider-specific URL
        import os
        self.endpoint = os.getenv('AZURE_SEARCH_ENDPOINT', endpoint)
        self.client = httpx.AsyncClient(timeout=10.0)
        
    async def search(self, query: str, count: int = 5, market: str = "en-US") -> List[Dict]:
        """Perform an Azure Search web query.

        Args:
            query: Search query string
            count: Number of results to return (max 50)
            market: Market/locale for search results

        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            raise ValueError("Azure Search API key is required for web search")

        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "User-Agent": "SkynetLite/1.0"
        }

        params = {
            "q": query,
            "count": min(count, 50),  # API limit
            "mkt": market,
            "responseFilter": "Webpages",
            "safeSearch": "Moderate"
        }

        try:
            response = await self.client.get(self.endpoint, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            web_pages = data.get("webPages", {})
            results = web_pages.get("value", [])

            # Format results for easier consumption
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("name", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "display_url": result.get("displayUrl", "")
                })

            return formatted_results

        except httpx.HTTPError as e:
            print(f"❌ Azure Search API error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected search error: {e}")
            return []
        
    
    async def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        """
        Search and create a summary of results
        
        Args:
            query: Search query
            max_results: Maximum number of results to include in summary
            
        Returns:
            Formatted summary string
        """
        results = await self.search(query, count=max_results)
        
        if not results:
            return f"Sorry, I couldn't find any information about '{query}'"
        
        summary = f"Here's what I found about '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. **{result['title']}**\n"
            summary += f"   {result['snippet']}\n"
            summary += f"   Source: {result['display_url']}\n\n"
        
        return summary.strip()
    
    async def get_news(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for news articles specifically
        
        Args:
            query: News search query
            count: Number of news results
            
        Returns:
            List of news article dictionaries
        """
        if not self.api_key:
            raise ValueError("Azure Search API key is required for news search")

        news_endpoint = self.endpoint or ""
        # If a specific news endpoint is desired, set AZURE_SEARCH_NEWS_ENDPOINT env var
        news_endpoint = os.getenv('AZURE_SEARCH_NEWS_ENDPOINT', news_endpoint)
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "User-Agent": "SkynetLite/1.0"
        }
        
        params = {
            "q": query,
            "count": min(count, 100),  # News API limit
            "mkt": "en-US",
            "safeSearch": "Moderate",
            "sortBy": "Date"  # Get the latest news
        }
        
        try:
            response = await self.client.get(
                news_endpoint,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("value", [])
            
            # Format news results
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    "title": article.get("name", ""),
                    "url": article.get("url", ""),
                    "description": article.get("description", ""),
                    "provider": article.get("provider", [{}])[0].get("name", ""),
                    "published": article.get("datePublished", ""),
                    "image_url": article.get("image", {}).get("thumbnail", {}).get("contentUrl", "")
                })
            
            return formatted_articles
            
        except httpx.HTTPError as e:
            print(f"❌ Azure News API error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected news search error: {e}")
            return []
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Semantic Kernel compatible search engine
class AzureSearchEngine:
    """Semantic Kernel compatible wrapper for Azure/Bing Search"""

    def __init__(self, api_key: str, endpoint: Optional[str] = None):
        self.search_tool = AzureSearchTool(api_key=api_key, endpoint=endpoint)

    async def search_async(self, query: str, count: int = 5, offset: int = 0) -> str:
        """Search and return formatted results for Semantic Kernel"""
        results = await self.search_tool.search(query, count=count)

        if not results:
            return f"No results found for: {query}"

        formatted = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n{result['snippet']}\nURL: {result['url']}\n\n"

        return formatted.strip()


class DuckDuckGoSearchTool:
    """Privacy-focused DuckDuckGo search integration without API keys"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,  # Follow redirects automatically
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.instant_api_url = "https://api.duckduckgo.com/"
        self.search_url = "https://html.duckduckgo.com/html/"  # Use the correct endpoint
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def get_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get instant answer from DuckDuckGo API
        
        Args:
            query: Search query string
            
        Returns:
            Instant answer data or None if not available
        """
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        try:
            response = await self.client.get(self.instant_api_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for instant answer
            if data.get("Answer"):
                return {
                    "type": "answer",
                    "answer": data["Answer"],
                    "answer_type": data.get("AnswerType", ""),
                    "definition": data.get("Definition", ""),
                    "abstract": data.get("Abstract", ""),
                    "abstract_source": data.get("AbstractSource", ""),
                    "abstract_url": data.get("AbstractURL", "")
                }
            
            # Check for definition
            elif data.get("Definition"):
                return {
                    "type": "definition",
                    "definition": data["Definition"],
                    "definition_source": data.get("DefinitionSource", ""),
                    "definition_url": data.get("DefinitionURL", "")
                }
            
            # Check for abstract
            elif data.get("Abstract"):
                return {
                    "type": "abstract",
                    "abstract": data["Abstract"],
                    "abstract_source": data.get("AbstractSource", ""),
                    "abstract_url": data.get("AbstractURL", "")
                }
            
            return None
            
        except Exception as e:
            print(f"❌ DuckDuckGo Instant API error: {e}")
            return None
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using DuckDuckGo HTML scraping
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
        """
        params = {
            "q": query,
            "kl": "us-en",  # Language/region
            "s": "0",       # Start index
        }
        
        try:
            response = await self.client.get(self.search_url, params=params)
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # Look for result containers - DuckDuckGo uses different selectors
            result_containers = soup.find_all('div', class_='web-result')
            if not result_containers:
                # Fallback to generic result containers
                result_containers = soup.find_all('div', {'class': re.compile(r'result')})
            
            for container in result_containers[:max_results]:
                try:
                    # Extract title and URL
                    title_element = container.find('a', {'class': re.compile(r'result-title|result__a')})
                    if not title_element:
                        # Alternative selector
                        title_element = container.find('a')
                    
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    url = title_element.get('href', '')
                    
                    # Clean up DuckDuckGo redirect URLs
                    if url.startswith('/l/?uddg='):
                        import urllib.parse
                        url = urllib.parse.unquote(url.split('uddg=')[1])
                    elif url.startswith('//duckduckgo.com/l/?uddg='):
                        import urllib.parse
                        url = urllib.parse.unquote(url.split('uddg=')[1])
                    
                    # Extract snippet
                    snippet = ""
                    snippet_element = container.find('span', {'class': re.compile(r'result-snippet|result__snippet')})
                    if snippet_element:
                        snippet = snippet_element.get_text(strip=True)
                    else:
                        # Alternative snippet extraction
                        snippet_element = container.find('div', {'class': re.compile(r'snippet')})
                        if snippet_element:
                            snippet = snippet_element.get_text(strip=True)
                    
                    if title and url and not url.startswith('/'):
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "display_url": url
                        })
                        
                except Exception as e:
                    print(f"Warning: Error parsing result: {e}")
                    continue
            
            # If no results found with specific selectors, try a more general approach
            if not results:
                # Look for any links that might be results
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Skip internal DuckDuckGo links and empty text
                    if (not href.startswith('/') and 
                        not href.startswith('//duckduckgo.com') and 
                        text and 
                        len(text) > 10 and
                        'http' in href):
                        
                        results.append({
                            "title": text,
                            "url": href,
                            "snippet": "",
                            "display_url": href
                        })
                        
                        if len(results) >= max_results:
                            break
            
            return results
            
        except httpx.HTTPError as e:
            print(f"❌ DuckDuckGo search error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected search error: {e}")
            return []
    
    async def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        """
        Search and create a summary of results, including instant answers
        
        Args:
            query: Search query
            max_results: Maximum number of results to include in summary
            
        Returns:
            Formatted summary string
        """
        # Try instant answer first
        instant_answer = await self.get_instant_answer(query)
        summary_parts = []
        
        if instant_answer:
            if instant_answer["type"] == "answer" and instant_answer.get("answer"):
                summary_parts.append(f"**Quick Answer:** {instant_answer['answer']}")
            elif instant_answer["type"] == "definition" and instant_answer.get("definition"):
                summary_parts.append(f"**Definition:** {instant_answer['definition']}")
            elif instant_answer["type"] == "abstract" and instant_answer.get("abstract"):
                summary_parts.append(f"**Summary:** {instant_answer['abstract']}")
        
        # Get regular search results
        results = await self.search(query, max_results=max_results)
        
        if not results and not summary_parts:
            return f"Sorry, I couldn't find any information about '{query}'"
        
        if summary_parts:
            summary = "\n".join(summary_parts) + "\n\n"
        else:
            summary = f"Here's what I found about '{query}':\n\n"
        
        if results:
            for i, result in enumerate(results, 1):
                summary += f"{i}. **{result['title']}**\n"
                if result['snippet']:
                    summary += f"   {result['snippet']}\n"
                summary += f"   Source: {result['url']}\n\n"
        
        return summary.strip()
    
    async def search_recent_news(self, topic: str, max_results: int = 3) -> str:
        """
        Search for recent news on a topic
        
        Args:
            topic: News topic to search
            max_results: Maximum results
            
        Returns:
            Recent news summary
        """
        # Add news-specific keywords to the search
        news_query = f"{topic} news recent latest"
        return await self.search_and_summarize(news_query, max_results)


class DuckDuckGoInstantAnswerTool:
    """Lightweight tool for DuckDuckGo instant answers only"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.api_url = "https://api.duckduckgo.com/"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def get_instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Get instant answer only"""
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1"
        }
        
        try:
            response = await self.client.get(self.api_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ DuckDuckGo Instant API error: {e}")
            return None


class GoogleSearchTool:
    """Google Custom Search JSON API integration.

    Requires environment variables: GOOGLE_API_KEY and GOOGLE_CX (Custom Search Engine ID).
    This uses the official Custom Search JSON API and therefore requires an API key
    and a CSE/engine id (cx).
    """

    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.cx = cx or os.getenv('GOOGLE_CX')
        self.endpoint = 'https://www.googleapis.com/customsearch/v1'
        self.client = httpx.AsyncClient(timeout=15.0)

    async def close(self):
        await self.client.aclose()

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key or not self.cx:
            raise ValueError('Google API key and CX are required for GoogleSearchTool')

        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': query,
            'num': min(max_results, 10),
        }

        try:
            resp = await self.client.get(self.endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get('items', [])
            results = []
            for it in items[:max_results]:
                results.append({
                    'title': it.get('title', ''),
                    'url': it.get('link', ''),
                    'snippet': it.get('snippet', ''),
                    'display_url': it.get('displayLink', it.get('link', ''))
                })

            return results

        except httpx.HTTPError as e:
            print(f"❌ Google Custom Search error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected Google search error: {e}")
            return []

    async def search_and_summarize(self, query: str, max_results: int = 3) -> str:
        results = await self.search(query, max_results=max_results)
        if not results:
            return f"Sorry, I couldn't find any information about '{query}'"

        summary = f"Here's what I found about '{query}':\n\n"
        for i, r in enumerate(results, 1):
            summary += f"{i}. **{r['title']}**\n"
            if r.get('snippet'):
                summary += f"   {r['snippet']}\n"
            summary += f"   Source: {r['display_url']}\n\n"

        return summary.strip()


# Factory function for search tool creation
async def create_search_tool(provider: str = "duckduckgo", use_instant_only: bool = False) -> Any:
    """
    Create appropriate search tool based on configuration
    
    Args:
        provider: Search provider ("duckduckgo", "bing")
        use_instant_only: Whether to use instant answer API only
        
    Returns:
        Configured search tool instance
    """
    p = provider.lower() if provider else "duckduckgo"
    if p == "duckduckgo":
        if use_instant_only:
            return DuckDuckGoInstantAnswerTool()
        else:
            return DuckDuckGoSearchTool()
    elif p in ("bing", "azure"):
        # Map legacy 'bing' to Azure Search; look for Azure or legacy env vars
        import os
        api_key = os.getenv('AZURE_SEARCH_KEY') or os.getenv('AZURE_SEARCH_API_KEY') or os.getenv('BING_API_KEY')
        endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        if not api_key:
            print("⚠️ Azure/Bing API key not found, falling back to DuckDuckGo")
            return DuckDuckGoSearchTool()
        return AzureSearchTool(api_key=api_key, endpoint=endpoint)
    elif p == "google":
        # Google Custom Search integration (requires GOOGLE_API_KEY + GOOGLE_CX)
        import os
        api_key = os.getenv('GOOGLE_API_KEY')
        cx = os.getenv('GOOGLE_CX')
        if not api_key or not cx:
            print("⚠️ Google API key or CX not found, falling back to DuckDuckGo")
            return DuckDuckGoSearchTool()
        return GoogleSearchTool(api_key=api_key, cx=cx)
    else:
        # Default to DuckDuckGo
        return DuckDuckGoSearchTool()
