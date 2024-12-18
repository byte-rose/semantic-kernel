import os
import requests
from dotenv import load_dotenv
from typing import Optional
from semantic_kernel.kernel_pydantic import KernelBaseModel

load_dotenv()

class CodeExecutionRequest(KernelBaseModel):
    source_code: str
    language_id: int
    stdin: Optional[str] = ""

class CodeExecutor:
    def __init__(self):
        self.judge0_api_key = os.getenv("JUDGE0_API_KEY")
        self.judge0_api_url = "https://judge0-ce.p.rapidapi.com"

    def validate_code(self, code: str) -> bool:
        """
        Validates the code for unsafe operations.

        Args:
            code: The code to validate.

        Returns:
            True if the code is safe, False otherwise.
        """
        unsafe_operations = ["os.", "subprocess.", "sys."]  # Customize as needed
        return all(op not in code for op in unsafe_operations)

    def execute_code(self, request: CodeExecutionRequest) -> str:
        """
        Executes code using the Judge0 API.

        Args:
            request: The code execution request.

        Returns:
            The result of the code execution.
        """
        if not self.validate_code(request.source_code):
            return "Code failed safety validation"

        headers = {
            "content-type": "application/json",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": self.judge0_api_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }

        payload = {
            "language_id": request.language_id,
            "source_code": request.source_code,
            "stdin": request.stdin
        }

        try:
            # Create a submission
            response = requests.post(f"{self.judge0_api_url}/submissions", json=payload, headers=headers)
            response.raise_for_status()
            token = response.json()["token"]

            # Check the submission status until it's completed
            while True:
                status_response = requests.get(f"{self.judge0_api_url}/submissions/{token}", headers=headers)
                status_response.raise_for_status()
                result = status_response.json()

                # Check if the submission is still processing
                if result["status"]["id"] in [1, 2]:  # 1: In Queue, 2: Processing
                    continue
                
                # Submission completed, check the result
                if result["status"]["id"] == 3:  # Accepted
                    return result["stdout"] or "Code executed successfully (no output)"
                else:
                    return f"Execution error: {result['status']['description']}\n{result.get('stderr', '')}"
        except requests.RequestException as e:
            return f"Error communicating with Judge0: {str(e)}"