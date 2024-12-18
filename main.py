import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel
from semantic_kernel.functions.kernel_function import KernelFunction

from code_executor_plugin import create_code_executor_plugin

# Load environment variables
load_dotenv()

# Initialize the kernel
kernel = Kernel()

# Configure Azure OpenAI service
service_id = "azure-chat-gpt"
chat_service = AzureChatCompletion(
    service_id=service_id,
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)
kernel.add_service(chat_service)

# Add plugins
# Create the CodeExecutorPlugin using the factory function
code_executor_function = create_code_executor_plugin(kernel)
kernel.add_plugin(code_executor_function, "CodeExecutor")
kernel.add_plugin(TimePlugin(), "Time")  # For other general tasks

# Define the chat function
chat_function = kernel.add_function(
    prompt="""You are a helpful assistant. Use the available functions when necessary to assist the user.
    If the user asks for code execution or calculations, use the CodeExecutor.execute_python_code function.

    {{$chat_history}}
    Human: {{$user_input}}
    Assistant: """,
    plugin_name="ChatBot",
    function_name="Chat",
    description="This is the main chat function that interacts with the user. It uses available functions to answer questions, execute code, and provide assistance."
)

# Execution settings for the chat function
req_settings = AzureChatPromptExecutionSettings(service_id=service_id, tool_choice="auto")
req_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={"excluded_plugins": ["ChatBot"]})

arguments = KernelArguments(settings=req_settings)

# Chat history
history = ChatHistory()

async def chat() -> bool:
    """
    Handles a single chat interaction with the user.
    """
    try:
        user_input = input("You:> ")
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting chat...")
        return False

    if user_input.lower() == "exit":
        print("\n\nExiting chat...")
        return False

    arguments["chat_history"] = history
    arguments["user_input"] = user_input
    answer = await kernel.invoke(
        function=chat_function,
        arguments=arguments,
    )
    print(f"Assistant:> {answer}")
    history.add_user_message(user_input)
    history.add_assistant_message(str(answer))
    return True

async def main() -> None:
    """
    Main function to run the chatbot.
    """
    print(
        "Welcome to the Azure OpenAI chat with Code Execution!\n"
        "  Type 'exit' to exit.\n"
        "  Ask questions, request calculations, or ask for code execution."
    )
    chatting = True
    while chatting:
        chatting = await chat()

if __name__ == "__main__":
    asyncio.run(main())