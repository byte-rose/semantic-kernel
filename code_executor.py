import os
import requests
from typing import Dict, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

class CodeExecutionRequest(BaseModel):
    source_code: str
    language_id: int  # Judge0 language ID
    stdin: Optional[str] = None
    expected_output: Optional[str] = None

class CodeExecutor:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("JUDGE0_API_KEY")
        self.base_url = "https://judge0-ce.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }

    def execute_code(self, request: CodeExecutionRequest) -> Dict:
        """
        Execute code using Judge0 API with safety checks
        """
        # Prepare submission
        submission_data = {
            "source_code": request.source_code,
            "language_id": request.language_id,
            "stdin": request.stdin,
            "expected_output": request.expected_output,
            # Safety constraints
            "cpu_time_limit": "2",  # 2 seconds
            "memory_limit": "128000",  # 128MB
            "enable_network": False
        }

        # Create submission
        response = requests.post(
            f"{self.base_url}/submissions",
            json=submission_data,
            headers=self.headers
        )
        token = response.json().get("token")

        # Get results
        result = requests.get(
            f"{self.base_url}/submissions/{token}",
            headers=self.headers
        )
        
        return result.json()

    def validate_code(self, code: str) -> bool:
        """
        Implement code validation logic here
        Returns True if code passes safety checks
        """
        # Example basic checks
        dangerous_terms = [
            "os.system", "subprocess", "eval(", "exec(",
            "import os", "import subprocess", "__import__"
        ]
        
        return not any(term in code for term in dangerous_terms)
