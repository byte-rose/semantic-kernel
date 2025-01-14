import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from plugins.adminplugin import AdminPlugin
from plugins.contentplugin import ContentPlugin
from utils.logging_config import setup_logging, log_separator
import logging
##TODO: Move to Azure OpenAI assistants 

# Set up logging
logger = setup_logging(console_level=logging.INFO, file_level=logging.DEBUG)

# Define agent configuration
AGENT_NAME = "BloggingAgent"
AGENT_INSTRUCTIONS = """
You are an AI blogging assistant passionate about creating high-quality blog posts on AI and security topics. Your work is crucial in educating readers and influencing industry standards.

Your workflow involves:
1. Discovering trending topics using SERP API, focusing on relevance and impact.
2. Conducting in-depth research using Tavily, ensuring accuracy and credibility.
3. Generating well-structured and engaging blog posts.
4. Publishing drafts to the Ghost blog platform with attention to detail.

When generating blog posts, follow this structured approach:
- Start with an engaging title that captures the essence of the topic.
- Provide a clear and concise introduction, setting the stage for the discussion.
- Develop the main content logically, ensuring each section flows seamlessly.
- Conclude with insightful takeaways, encouraging further thought and discussion.
- Include proper source citations to enhance credibility and trustworthiness.

Maintain a professional tone throughout, and remember that your insights can shape the future of AI and security discourse.
"""

async def invoke_agent(agent: ChatCompletionAgent, input: str, chat: ChatHistory) -> None:
    """Invoke the agent with the user input."""
    chat.add_user_message(input)
    logger.info(f"# {AuthorRole.USER}: '{input}'")

    try:
        contents = []
        content_name = ""
        async for content in agent.invoke_stream(chat):
            content_name = content.name
            contents.append(content)
        message_content = "".join([content.content for content in contents])
        logger.info(f"# {content.role} - {content_name or '*'}: '{message_content}'")
        chat.add_assistant_message(message_content)
    except Exception as e:
        logger.error(f"Error during agent invocation: {str(e)}")
        raise

async def main():
    try:
        log_separator(logger, "Initializing Semantic Kernel", logging.INFO)
        
        # Load environment variables
        load_dotenv()
        
        # Azure OpenAI Configuration
        endpoint = "https://ujao-ai.openai.azure.com"
        deployment = "gpt-4o-2"
        api_version = "2024-08-01-preview"
        api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

        # Initialize kernel and configure AI service
        kernel = Kernel()
        service_id = "blogging_agent"
        
        azure_chat_service = AzureChatCompletion(
            service_id=service_id,
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        kernel.add_service(azure_chat_service)
        logger.info("Azure OpenAI service configured successfully")

        # Configure function choice behavior
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        # Import plugins
        log_separator(logger, "Importing Plugins")
        kernel.add_plugin(AdminPlugin(), plugin_name="admin")
        kernel.add_plugin(ContentPlugin(), plugin_name="content")
        logger.info("Plugins imported successfully")

        # Create agent and chat history
        agent = ChatCompletionAgent(
            service_id=service_id,
            kernel=kernel,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            execution_settings=settings
        )
        chat = ChatHistory()

        # Print welcome message
        logger.info("\nWelcome to the AI Blog Generator!")
        logger.info("You can ask me to:")
        logger.info("- Find trending topics")
        logger.info("- Research a specific topic")
        logger.info("- Generate a blog post")
        logger.info("- Post a draft")
        logger.info("Type 'exit' to quit\n")

        # Interactive chat loop
        while True:
            user_input = input("\nWhat would you like me to do? > ")
            if user_input.lower() == 'exit':
                break
            await invoke_agent(agent, user_input, chat)

    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.exception("An error occurred during execution")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
        logger.info("Program completed successfully")
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Program terminated with error: {str(e)}")
