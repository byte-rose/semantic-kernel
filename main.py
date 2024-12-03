import semantic_kernel as sk
from semantic_kernel.connectors.ai import OpenAITextCompletion
from code_executor import CodeExecutor, CodeExecutionRequest
import asyncio
import os
from dotenv import load_dotenv

async def main():
    # Initialize Semantic Kernel
    kernel = sk.Kernel()
    
    # Load environment variables
    load_dotenv()
    
    # Configure AI service
    api_key = os.getenv("OPENAI_API_KEY")
    deployment = os.getenv("OPENAI_DEPLOYMENT_NAME", "text-davinci-003")
    service = OpenAITextCompletion(deployment, api_key)
    kernel.add_text_completion_service("openai", service)

    # Create semantic function for code generation
    prompt = """
    Write a Python function that {{$input}}.
    Only return the code, no explanations.
    The code should be safe and not use any system calls or dangerous operations.
    """
    
    code_generation = kernel.create_semantic_function(prompt)

    # Example: Generate a function that calculates fibonacci sequence
    user_request = "calculates the fibonacci sequence up to n terms"
    generated_code = await code_generation(user_request)
    
    # Initialize code executor
    executor = CodeExecutor()
    
    # Validate generated code
    if executor.validate_code(str(generated_code)):
        # Execute code with test input
        request = CodeExecutionRequest(
            source_code=str(generated_code),
            language_id=71,  # Python3
            stdin="10"  # Test with first 10 fibonacci numbers
        )
        
        result = executor.execute_code(request)
        print("Generated Code:")
        print(generated_code)
        print("\nExecution Result:")
        print(result)
    else:
        print("Generated code failed safety validation")

if __name__ == "__main__":
    asyncio.run(main())
