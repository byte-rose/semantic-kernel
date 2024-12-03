<<<<<<< HEAD
# semantic-kernel
=======
# Semantic Kernel Code Execution with Judge0

This project demonstrates safe code execution using Microsoft's Semantic Kernel and the Judge0 API. It shows how to:
1. Use Semantic Kernel to generate code
2. Safely validate and execute code using Judge0 API
3. Handle execution results and potential security concerns

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Judge0 API credentials:
```
JUDGE0_API_KEY=your_api_key_here
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
