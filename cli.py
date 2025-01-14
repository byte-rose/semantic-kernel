#!/usr/bin/env python3

import os
import click
import asyncio
import re
from dotenv import load_dotenv
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from plugins.adminplugin import AdminPlugin
from plugins.contentplugin import ContentPlugin
from utils.logging_config import setup_logging, log_separator
from utils.state_manager import StateManager
import logging

# Set up logging
logger = setup_logging(console_level=logging.INFO, file_level=logging.DEBUG)

# Initialize state manager
state = StateManager()

# Agent configuration
AGENT_NAME = "BloggingAgent"
AGENT_INSTRUCTIONS = """
You are an AI blogging assistant that specializes in creating high-quality blog posts about AI and security topics.
Your workflow involves:
1. Finding trending topics using SERP API
2. Researching topics in depth using Tavily
3. Generating well-structured blog posts
4. Publishing drafts to Ghost blog platform

Always maintain a professional tone and ensure all content is properly sourced.
"""

def extract_topics(content: str) -> list[str]:
    """Extract numbered topics from content."""
    topics = []
    lines = content.split('\n')
    for line in lines:
        # Match lines starting with a number followed by a dot
        if re.match(r'^\d+\.?\s+(.+)$', line.strip()):
            topic = re.sub(r'^\d+\.?\s+', '', line.strip())
            # Clean up markdown and extra characters
            topic = re.sub(r'[\*\#\`]', '', topic).strip()
            topics.append(topic)
    return topics

async def setup_agent():
    """Initialize and configure the blogging agent."""
    try:
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
        kernel.add_plugin(AdminPlugin(), plugin_name="admin")
        kernel.add_plugin(ContentPlugin(), plugin_name="content")

        # Create agent
        agent = ChatCompletionAgent(
            service_id=service_id,
            kernel=kernel,
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
            execution_settings=settings
        )
        
        # Create chat history and populate with previous messages
        chat = ChatHistory()
        for msg in state.get_chat_history():
            if msg['role'] == 'user':
                chat.add_user_message(msg['content'])
            else:
                chat.add_assistant_message(msg['content'])
        
        return agent, chat
        
    except Exception as e:
        logger.exception("Failed to initialize agent")
        raise

async def process_stream(stream, chat):
    """Process the async stream and collect the response."""
    contents = []
    content_name = ""
    async for content in stream:
        content_name = content.name
        contents.append(content)
        # Print each chunk as it arrives
        click.echo(content.content, nl=False)
    
    message_content = "".join([content.content for content in contents])
    chat.add_assistant_message(message_content)
    state.add_message('assistant', message_content)
    
    # If this was a topics request, store the topics
    if "trending topics" in chat.messages[-2].content.lower():
        topics = extract_topics(message_content)
        if topics:
            state.add_topics(topics)
    
    click.echo()  # Add newline at the end

@click.group()
def cli():
    """AI-powered blogging assistant for creating and managing blog posts."""
    pass

@cli.command()
def topics():
    """List trending AI and security topics."""
    async def run():
        agent, chat = await setup_agent()
        chat.add_user_message("Find trending topics")
        state.add_message('user', "Find trending topics")
        stream = agent.invoke_stream(chat)
        await process_stream(stream, chat)
        
    asyncio.run(run())

@cli.command()
@click.argument('topic')
def research(topic):
    """Research a specific topic."""
    async def run():
        agent, chat = await setup_agent()
        message = f"Research the topic: {topic}"
        chat.add_user_message(message)
        state.add_message('user', message)
        stream = agent.invoke_stream(chat)
        await process_stream(stream, chat)
        
    asyncio.run(run())

@cli.command()
@click.argument('topic')
@click.option('--tone', default='technical', help='Writing tone (professional/casual/technical)')
def blog(topic, tone):
    """Generate a blog post about a topic."""
    async def run():
        agent, chat = await setup_agent()
        message = f"Generate a {tone} blog post about: {topic}"
        chat.add_user_message(message)
        state.add_message('user', message)
        stream = agent.invoke_stream(chat)
        await process_stream(stream, chat)
        
    asyncio.run(run())

@cli.command()
@click.argument('title')
@click.argument('content', required=False)
def publish(title, content):
    """Publish a blog post to Ghost."""
    async def run():
        agent, chat = await setup_agent()
        if content:
            message = f"Post this content as a draft titled '{title}': {content}"
        else:
            message = f"Generate and post a draft blog about: {title}"
        chat.add_user_message(message)
        state.add_message('user', message)
        stream = agent.invoke_stream(chat)
        await process_stream(stream, chat)
        
    asyncio.run(run())

@cli.command()
def interactive():
    """Start an interactive chat session."""
    async def run():
        agent, chat = await setup_agent()
        
        click.echo("Welcome to the AI Blog Generator!")
        click.echo("\nStored Topics:")
        topics = state.get_topics()
        if topics:
            for i, topic in enumerate(topics, 1):
                click.echo(f"{i}. {topic}")
        else:
            click.echo("No topics stored. Use 'topics' command to find trending topics.")
        
        click.echo("\nCommands:")
        click.echo("- Find trending topics")
        click.echo("- Research [topic]")
        click.echo("- Generate blog about [topic]")
        click.echo("- Post draft [title]")
        click.echo("Type 'exit' to quit\n")
        
        while True:
            user_input = click.prompt("What would you like me to do?")
            if user_input.lower() == 'exit':
                break
            chat.add_user_message(user_input)
            state.add_message('user', user_input)
            stream = agent.invoke_stream(chat)
            await process_stream(stream, chat)
            
    asyncio.run(run())

@cli.command()
def history():
    """Show chat history."""
    for msg in state.get_chat_history():
        role = "🤖" if msg['role'] == 'assistant' else "👤"
        click.echo(f"\n{role} [{msg['timestamp']}]")
        click.echo(msg['content'])

@cli.command()
def clear():
    """Clear chat history."""
    state.clear_history()
    click.echo("Chat history cleared.")

if __name__ == '__main__':
    cli()
