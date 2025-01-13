import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from tavily import TavilyClient
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing import Annotated
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class ResearchPlugin:
    """
    Plugin for researching topics using SERP API and Tavily.
    
    This plugin handles topic discovery and in-depth research using multiple sources.
    """

    def __init__(self):
        load_dotenv()
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if not self.serp_api_key:
            raise ValueError("SERPAPI_KEY environment variable is not set.")
        if not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set.")
            
        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)

    @kernel_function(description="Get trending AI and security topics using SERP API")
    def get_topics(self) -> Annotated[str, "List of trending topics"]:
        try:
            params = {
                "engine": "google",
                "q": "latest artificial intelligence security trends",
                "api_key": self.serp_api_key,
                "num": 5,
                "tbs": "qdr:w"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            topics = []
            for result in results.get("organic_results", []):
                topics.append(f"- {result['title']}")
                
            return "\n".join(topics)
            
        except Exception as e:
            error_msg = f"Error getting topics: {str(e)}"
            logger.exception(error_msg)
            return error_msg

    @kernel_function(description="Research a specific topic using Tavily")
    def research_topic(
        self,
        topic: Annotated[str, "The topic to research"]
    ) -> Annotated[dict, "Research data including content and sources"]:
        try:
            search_result = self.tavily_client.search(
                query=topic,
                search_depth="deep",
                include_answer=True,
                include_raw_content=True
            )
            
            research_data = {
                'topic': topic,
                'content': search_result.get('answer', ''),
                'sources': []
            }
            
            for source in search_result.get('sources', [])[:3]:
                research_data['sources'].append({
                    'title': source.get('title'),
                    'url': source.get('url')
                })
                
            return research_data
            
        except Exception as e:
            error_msg = f"Error researching topic: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}
