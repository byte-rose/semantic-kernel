import os
from dotenv import load_dotenv
import requests
import json
import logging
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing import Annotated
from utils.logging_config import setup_logging, log_separator, pretty_print_json

# Set up logging for this module
logger = setup_logging(console_level=logging.INFO, file_level=logging.DEBUG)

class ContentPlugin:
    """
    A plugin that handles all content-related operations for the blogging agent.
    
    This plugin is responsible for:
    1. Finding trending topics using SERP API (when API key is available)
    2. Conducting research using Tavily's AI research engine
    3. Generating well-structured blog posts
    
    It gracefully falls back to mock data when API keys aren't available,
   
    """

    def __init__(self):
        """
        Initialize the ContentPlugin with necessary API keys.
        
        Loads API keys from environment variables:
        - SERPAPI_KEY: For finding trending topics
        - TAVILY_API_KEY: For AI-powered research
        
        If keys aren't found, the plugin will use mock data instead.
        """
        load_dotenv()
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        # Let a users know if we're using mock data
        if not self.serpapi_key:
            logger.warning("SERPAPI_KEY not set. We'll use example topics for now.")
        if not self.tavily_key:
            logger.warning("TAVILY_API_KEY not set. We'll use example research data for now.")


##TODO: Immplement topic research and generation based on a scheduler.
    @kernel_function(description="Get trending blog topics")
    def get_trending_topics(self) -> str:
        """
        Find trending topics in AI and security using SERP API.
        
        This function:
        1. Queries SERP API for trending topics (when API key is available)
        2. Falls back to curated example topics for development/testing
        3. Returns topics in a numbered list format
        
        Returns:
            str: A numbered list of trending topics, e.g:
                1. AI Security in Cloud Computing
                2. Zero Trust Architecture
                etc.
        """
        try:
            log_separator(logger, "Getting Trending Topics", logging.INFO)
            
            # For now, we're using carefully curated example topics
            # TODO: Implement real SERP API call when ready for production
            topics = [
                "AI Security in Cloud Computing",
                "Zero Trust Architecture",
                "Machine Learning for Threat Detection",
                "AI Governance and Regulation",
                "Quantum Computing Security"
                "Large Language Models for Security",
                "Large Language Models pentesting",
                "The threat Landscape of Enterprise AI",
                "Blue Teaming with Large Language Models",
                "Red Teaming with Large Language Models",
            ]
            
            # Format topics as a numbered list
            result = "\n".join(f"{i+1}. {topic}" for i, topic in enumerate(topics))
            logger.info("✨ Successfully found trending topics")
            logger.debug(f"Topics:\n{result}")
            
            return result
            
        except Exception as e:
            error_msg = f"😟 Couldn't get trending topics: {str(e)}"
            logger.exception(error_msg)
            return error_msg

    @kernel_function(description="Research a specific topic using Tavily")
    def research_topic(
        self,
        topic: Annotated[str, "The topic to research"]
    ) -> str:
        """
        Conduct in-depth research on a topic using Tavily's AI research engine.
        
        This function:
        1. Takes a topic as input
        2. Uses Tavily API to gather comprehensive research (when API key is available)
        3. Falls back to example research data for development/testing
        
        Args:
            topic (str): The topic to research, e.g., "AI Security in Cloud Computing"
        
        Returns:
            str: Detailed research about the topic, including key points,
                trends, and expert opinions
        """
        try:
            log_separator(logger, f"Researching: {topic}", logging.INFO)
            
            if self.tavily_key:
                from tavily import TavilyClient
                
                # Initialize Tavily client
                client = TavilyClient(api_key=self.tavily_key)
                
                # Perform research using Tavily
                search_result = client.search(
                    query=topic,
                    search_depth="advanced",
                    include_answer=True,
                    include_raw_content=False,
                    max_results=5,
                    include_domains=["arxiv.org", "github.com", "microsoft.com", "google.com", "openai.com"],
                    exclude_domains=["youtube.com", "facebook.com", "twitter.com"]
                )
                
                # Extract the AI-generated answer
                if search_result.get('answer'):
                    research = search_result['answer']
                else:
                    # Format results if no AI answer
                    research = "Research Findings:\n\n"
                    for result in search_result.get('results', []):
                        research += f"- {result.get('title', 'Untitled')}\n"
                        research += f"  {result.get('content', 'No content available')}\n\n"
                
                logger.info("🔍 Tavily research completed successfully")
                
            else:
                logger.warning("Using mock research data (TAVILY_API_KEY not set)")
                research = f"""
                Here's what we know about {topic}:
                
                Key Points:
                - Latest trends and developments
                - Expert insights and analysis
                - Real-world applications
                - Future implications
                
                The field of {topic} is rapidly evolving, with new developments emerging regularly.
                Experts suggest focusing on practical implementations while keeping security in mind.
                """
            
            logger.debug(f"Research results:\n{research}")
            return research
            
        except Exception as e:
            error_msg = f"😟 Research failed: {str(e)}"
            logger.exception(error_msg)
            return error_msg

    @kernel_function(description="Generate a blog post from given content")
    def generate_blog(
        self,
        title: Annotated[str, "The title for the blog post"],
        content: Annotated[str, "The research or content to base the blog on"]
    ) -> str:
        """
        Transform research content into a well-structured blog post.
        
        This function:
        1. Takes a title and research content
        2. Structures it into a proper blog format with sections
        3. Adds necessary formatting and metadata
        
        Args:
            title (str): The blog post title
            content (str): The research content to transform
        
        Returns:
            str: A formatted blog post with introduction, main content,
                and conclusion sections
        """
        try:
            log_separator(logger, f"Creating Blog Post: {title}", logging.INFO)
            
            # Create a well-structured blog post
            blog_post = f"""
# {title}

## Introduction
An engaging introduction to {title}, highlighting its significance in today's rapidly evolving tech landscape.

## Main Content
{content}

## Conclusion
A thoughtful conclusion that summarizes key points and looks toward future developments.

---
Made with ❤️ in Kiambu, Kenya
            """
            
            logger.info("✍️ Blog post generated successfully")
            logger.debug(f"Blog content:\n{blog_post}")
            
            return blog_post
            
        except Exception as e:
            error_msg = f"😟 Blog generation failed: {str(e)}"
            logger.exception(error_msg)
            return error_msg

    @kernel_function(description="Generate a blog post from a topic")
    def generate_blog_from_topic(
        self,
        topic: Annotated[str, "The topic to write about"],
        tone: Annotated[str, "The writing tone (e.g., professional, casual, technical)"] = "technical"
    ) -> str:
        """
        Create a complete blog post from just a topic.
        
        This is a convenience function that:
        1. Researches the topic automatically
        2. Generates a blog post from the research
        3. Maintains the specified tone throughout
        
        Args:
            topic (str): The topic to write about
            tone (str, optional): The desired writing tone. Defaults to "professional"
        
        Returns:
            str: A complete, well-structured blog post ready for publishing
        """
        try:
            log_separator(logger, f"Creating Blog from Topic: {topic}", logging.INFO)
            
            # First, let's research the topic
            logger.info("🔍 Starting research phase...")
            research = self.research_topic(topic)
            
            # Then, transform it into a blog post
            logger.info("✍️ Crafting the blog post...")
            blog_post = self.generate_blog(topic, research)
            
            return blog_post
            
        except Exception as e:
            error_msg = f"😟 Blog creation failed: {str(e)}"
            logger.exception(error_msg)
            return error_msg