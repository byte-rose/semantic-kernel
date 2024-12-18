from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel import Kernel, KernelFunction
from semantic_kernel.functions.kernel_arguments import KernelArguments

from code_executor import CodeExecutor, CodeExecutionRequest
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_function import KernelFunction
class CodeExecutorPlugin:
    def __init__(self, kernel: Kernel):
        self.executor = CodeExecutor()
        self.kernel = kernel

    @kernel_function(
        description="Execute Python code safely using Judge0",
        name="execute_python_code"
    )
    def execute_python_code(self, code: str) -> str:
        """
        Executes Python code using the CodeExecutor.

        Args:
            code: The Python code to execute.

        Returns:
            The result of the code execution.
        """
        request = CodeExecutionRequest(
            source_code=code,
            language_id=71,  # Python 3
            stdin=""
        )
        result = self.executor.execute_code(request)
        return f"Execution Result:\n{result}"

# Example of how to create the plugin using KernelPluginFactory
def create_code_executor_plugin(kernel: Kernel) -> KernelFunction:
    """
    Creates the CodeExecutorPlugin using KernelPluginFactory.

    Args:
        kernel: The Semantic Kernel instance.

    Returns:
        The CodeExecutorPlugin as a KernelFunction.
    """
    code_executor_plugin = CodeExecutorPlugin(kernel)

    # Create the KernelFunction using from_method
    execute_function = KernelFunction.from_method(
        method=code_executor_plugin.execute_python_code,
        plugin_name="CodeExecutorPlugin",
    )

    return execute_function