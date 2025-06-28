"""
Bing Search integration for Skynet Lite
Provides real-time web search capabilities
"""

import httpx
from typing import List, Dict, Optional


class BingSearchTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        self.client = httpx.AsyncClient(timeout=10.0)
        
    async def search(self, query: str, count: int = 5, market: str = "en-US") -> List[Dict]:
        """
        Perform a Bing web search
        
        Args:
            query: Search query string
            count: Number of results to return (max 50)
            market: Market/locale for search results
            
        Returns:
            List of search result dictionaries
        """
        if not self.api_key:
            raise ValueError("Bing API key is required for web search")
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "User-Agent": "SkynetLite/1.0"
        }
        
        params = {
            "q": query,
            "count": min(count, 50),  # Bing API limit
            "mkt": market,
            "responseFilter": "Webpages",
            "safeSearch": "Moderate"
        }
        
        try:
            response = await self.client.get(
                self.endpoint,
                headers=headers,
                params=params
            )
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
            print(f"❌ Bing Search API error: {e}")
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
            raise ValueError("Bing API key is required for news search")
        
        news_endpoint = "https://api.bing.microsoft.com/v7.0/news/search"
        
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
            print(f"❌ Bing News API error: {e}")
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
class BingSearchEngine:
    """Semantic Kernel compatible wrapper for Bing Search"""
    
    def __init__(self, api_key: str):
        self.search_tool = BingSearchTool(api_key)
    
    async def search_async(self, query: str, count: int = 5, offset: int = 0) -> str:
        """Search and return formatted results for Semantic Kernel"""
        results = await self.search_tool.search(query, count=count)
        
        if not results:
            return f"No results found for: {query}"
        
        formatted = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n{result['snippet']}\nURL: {result['url']}\n\n"
        
        return formatted.strip()
