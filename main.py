import asyncio
from typing import TYPE_CHECKING
from ghost_client import Ghost
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents import ChatHistory
from semantic_kernel.functions import KernelArguments
import os
from dotenv import load_dotenv


load_dotenv()

if TYPE_CHECKING:
    pass

# Ghost Blog API configuration
GHOST_API_URL = os.getenv("GHOST_API_URL")
GHOST_ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
GHOST_API_URL=os.getenv("GHOST_API_URL")

ghost_client = Ghost(api_url=GHOST_API_URL, api_key=GHOST_ADMIN_API_KEY)

# # System message for the blog-writing agent
# system_message = """
# You are a professional blog writer. Your task is to generate
# engaging and informative blog posts on various topics.
# When asked to write a blog post, you should provide a
# well-structured article with a title, introduction,
# main content, and conclusion.
# """

# Create and configure the kernel
kernel = Kernel()

# Define a function to post to Ghost Blog
def post_to_ghost(title, content):
    try:
        post = ghost_client.posts.create({
            'title': title,
            'content': content,
            'status': 'draft'  # You can change this to 'published' if you want to publish immediately
        })
        return f"Blog post '{title}' created successfully with id: {post['id']}"
    except Exception as e:
        return f"Error creating blog post: {str(e)}"

# Add the Ghost Blog function to the kernel
kernel.add_function(post_to_ghost, plugin_name="GhostBlog", function_name="PostBlog")

# Define a blog writing function
blog_writing_function = kernel.add_function(
    prompt="Write a blog post about {{$topic}}. Provide the title and content.",
    plugin_name="BlogWriter",
    function_name="WriteBlog",
)

# Configure your chat completion service here
# chat_completion_service, request_settings = get_chat_completion_service_and_request_settings(Services.YOUR_CHOSEN_SERVICE)

# Set up function choice behavior
request_settings = KernelArguments()
request_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

# kernel.add_service(chat_completion_service)

# Create a chat history
history = ChatHistory()
history.add_system_message(system_message)

async def generate_and_post_blog():
    topic = input("Enter a topic for the blog post: ")
    
    arguments = KernelArguments(settings=request_settings)
    arguments["topic"] = topic

    # Generate blog content
    result = await kernel.invoke(blog_writing_function, arguments=arguments)
    
    if result:
        blog_content = result.value[0]
        print("Generated blog content:")
        print(blog_content)

        # Extract title and content (you might need to adjust this based on the AI's output format)
        lines = blog_content.split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:]).strip()

        # Post to Ghost
        post_result = await kernel.invoke("GhostBlog", "PostBlog", KernelArguments(title=title, content=content))
        print(post_result)
    else:
        print("Failed to generate blog content.")

async def main():
    print("Welcome to the AI Blog Generator and Poster!")
    while True:
        await generate_and_post_blog()
        if input("Generate another blog? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    asyncio.run(main())
