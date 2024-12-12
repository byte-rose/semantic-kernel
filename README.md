<<<<<<< HEAD
# semantic-kernel
=======
# Semantic Kernel Code Execution with Judge0

This project demonstrates safe code execution using Microsoft's Semantic Kernel (with Azure OpenAI) and the Judge0 API. It shows how to:
1. Use Semantic Kernel with Azure OpenAI to generate code
2. Safely validate and execute code using Judge0 API
3. Handle execution results and potential security concerns

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API credentials:
```
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here

# Judge0 API Key (from RapidAPI)
JUDGE0_API_KEY=your_judge0_api_key_here
```

## Usage

Run the main script:
```bash
python main.py
```

## Security Notes

This project implements several safety measures:
- Code validation before execution
- Resource limits on execution
- Sandboxed environment through Judge0
- Input sanitization
>>>>>>> 3b16146 (Initial commit: Setup basic project structure with Semantic Kernel and Judge0 integration)
