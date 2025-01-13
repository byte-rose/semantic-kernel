import asyncio
from typing import Annotated
import os
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.kernel import Kernel
from dotenv import load_dotenv
from plugins.adminplugin import AdminPlugin
from plugins.researchplugin import ResearchPlugin
from plugins.generatorplugin import GeneratorPlugin

load_dotenv()

AGENT_NAME = "BloggingAgent"
AGENT_INSTRUCTIONS = """
You are an AI blogging assistant that specializes in creating high-quality blog posts about AI and security topics.
Your workflow involves:
1. Finding trending topics using SERP API
2. Researching topics in depth using Tavily
3. Generating well-structured blog posts
4. Publishing drafts to Ghost blog platform

Always maintain a professional tone and ensure all content is properly sourced.
When generating blog posts, include:
- Engaging titles
- Clear introduction
- Well-structured main content
- Proper conclusion
- Source citations
"""

class BlogWorkflowPlugin:
    """Plugin for managing the blog creation workflow."""

    @kernel_function(description="Get a list of trending AI and security topics")
    def get_trending_topics(self) -> Annotated[str, "Returns a list of trending topics"]:
        return """
        1. AI Security in Cloud Computing
        2. Zero Trust Architecture
        3. Machine Learning for Threat Detection
        4. AI Governance and Regulation
        5. Quantum Computing Security
        """

    @kernel_function(description="Research a specific topic")
    def research_topic(
        self, topic: Annotated[str, "The topic to research"]
    ) -> Annotated[str, "Returns detailed research about the topic"]:
        return f"Detailed research about {topic} would be conducted using Tavily API"

    @kernel_function(description="Generate a blog post")
    def generate_blog(
        self,
        title: Annotated[str, "The blog post title"],
        content: Annotated[str, "The research content to base the blog on"]
    ) -> Annotated[str, "Returns the generated blog post"]:
        return f"Generated blog post about {title} based on the research"

    @kernel_function(description="Post a blog draft")
    def post_draft(
        self,
        title: Annotated[str, "The blog post title"],
        content: Annotated[str, "The blog post content"]
    ) -> Annotated[str, "Returns the result of posting the draft"]:
        return f"Blog post '{title}' has been posted as a draft"

async def invoke_agent(agent: ChatCompletionAgent, input: str, chat: ChatHistory) -> None:
    """Invoke the agent with user input."""
    chat.add_user_message(input)
    print(f"\n# User: '{input}'")
    
    async for content in agent.invoke_stream(chat):
        if content.role != AuthorRole.TOOL:
            print(f"# Assistant: {content.content}")
    chat.add_assistant_message(content.content)

async def main():
    # Create kernel and register plugins
    kernel = Kernel()
    kernel.add_plugin(BlogWorkflowPlugin(), plugin_name="blog")
    kernel.add_plugin(AdminPlugin(), plugin_name="admin")
    kernel.add_plugin(ResearchPlugin(), plugin_name="research")
    kernel.add_plugin(GeneratorPlugin(), plugin_name="generator")

    # Add Azure Chat Completion service
    service_id = "blogging_agent"
    kernel.add_service(
        AzureChatCompletion(
            service_id=service_id,
            deployment_name="gpt-4o-2",
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview"
        )
    )

    # Configure settings
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create the agent
    agent = ChatCompletionAgent(
        service_id=service_id,
        kernel=kernel,
        name=AGENT_NAME,
        instructions=AGENT_INSTRUCTIONS,
        execution_settings=settings
    )

    # Create chat history
    chat = ChatHistory()

    try:
        print("Welcome to the AI Blog Generator!")
        print("You can ask me to:")
        print("- Find trending topics")
        print("- Research a specific topic")
        print("- Generate a blog post")
        print("- Post a draft")
        print("Type 'exit' to quit")

        while True:
            user_input = input("\nWhat would you like me to do? > ")
            if user_input.lower() == 'exit':
                break

            await invoke_agent(agent, user_input, chat)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
