import os
from dotenv import load_dotenv
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from typing import Annotated
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class GeneratorPlugin:
    """
    Plugin for generating blog posts using AI-powered tools.

    This plugin will use Azure OpenAI to generate a blog post based on given content or topic.
    """

    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")

    @kernel_function(description="Generate a blog post from given content")
    def generate_blog(
        self,
        title: Annotated[str, "The title for the blog post"],
        content: Annotated[str, "The research or content to base the blog on"]
    ) -> Annotated[dict, "Generated blog post with title and content"]:
        try:
            # Here you would typically use Azure OpenAI to generate the blog
            blog = {
                'title': title,
                'content': f"""
# {title}

## Introduction
{self._generate_introduction(title)}

## Main Content
{content}

## Conclusion
{self._generate_conclusion(content)}

---
This blog post was generated using AI-powered tools.
                """
            }
            
            return blog
            
        except Exception as e:
            error_msg = f"Error generating blog: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}

    @kernel_function(description="Generate a blog post from a topic")
    def generate_blog_from_topic(
        self,
        topic: Annotated[str, "The topic to write about"],
        tone: Annotated[str, "The writing tone (e.g., professional, casual, technical)"] = "professional"
    ) -> Annotated[dict, "Generated blog post with title and content"]:
        try:
            title = f"Understanding {topic}: A Comprehensive Guide"
            
            blog = {
                'title': title,
                'content': f"""
# {title}

## Introduction
A comprehensive look at {topic}, exploring its key aspects and implications.

## Main Content
Detailed discussion about {topic} would go here.
This would be generated using Azure OpenAI in a {tone} tone.

## Conclusion
Summary of key points about {topic}.

---
This blog post was generated using AI-powered tools.
                """
            }
            
            return blog
            
        except Exception as e:
            error_msg = f"Error generating blog: {str(e)}"
            logger.exception(error_msg)
            return {"error": error_msg}

    def _generate_introduction(self, title: str) -> str:
        # This would use Azure OpenAI to generate an introduction
        return f"An introduction to {title} and its significance in today's context."

    def _generate_conclusion(self, content: str) -> str:
        # This would use Azure OpenAI to generate a conclusion
        return "A thoughtful conclusion summarizing the key points and future implications."
