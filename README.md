# AI-Powered Ghost Blog Assistant

A powerful blogging assistant built with Semantic Kernel that helps you create, research, and manage blog posts on your Ghost platform.

## 🌟 Features

- **Content Research & Generation**
  - Find trending topics in AI and security
  - Conduct in-depth research using Tavily
  - Generate well-structured blog posts
  - Automatic content formatting for Ghost

- **Ghost Blog Integration**
  - Create and manage draft posts
  - Support for Ghost's Lexical format
  - Secure API authentication
  - Easy post management

- **AI-Powered Capabilities**
  - Azure OpenAI integration
  - Semantic search for topics
  - Natural language interaction
  - Smart content structuring

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- A Ghost blog instance
- Azure OpenAI API access
- (Optional) SERP API and Tavily API keys for enhanced research

### Installation

1. Clone the repository:
```bash
git clone this repo
cd ghost-blog-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
# Required
AZURE_OPENAI_API_KEY=your-api-key
GHOST_API_KEY=your-ghost-admin-api-key
GHOST_API_URL=https://your-ghost-blog.com/

# Optional (for enhanced research)
SERPAPI_KEY=your-serp-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### Usage

Run the assistant:
```bash
python main.py
```

Available commands:
- `Find trending topics`: Discover current AI and security topics
- `Research [topic]`: Conduct in-depth research on a topic
- `Generate blog post about [topic]`: Create a new blog post
- `Post draft`: Submit the generated content as a draft to Ghost

## 🔧 Architecture

### Components

1. **Main Application** (`main.py`)
   - Configures Semantic Kernel and Azure OpenAI
   - Manages the chat interface
   - Coordinates plugin interactions

2. **Content Plugin** (`plugins/contentplugin.py`)
   - Handles topic discovery
   - Manages research functionality
   - Generates blog content

3. **Admin Plugin** (`plugins/adminplugin.py`)
   - Manages Ghost blog integration
   - Handles post creation and updates
   - Formats content for Ghost's Lexical format

4. **Utilities** (`utils/`)
   - Logging configuration
   - Helper functions

### Technologies

- **Semantic Kernel**: Core framework for AI operations
- **Azure OpenAI**: Language model for content generation
- **Ghost API**: Blog platform integration
- **Tavily**: AI-powered research (optional)
- **SERP API**: Topic discovery (optional)

## 🔐 Security

- API keys are managed through environment variables
- Secure Ghost API authentication using JWT
- No sensitive data is stored in the code

## 🛠️ Development

### Adding New Features

1. Create a new plugin in the `plugins/` directory
2. Register the plugin in `main.py`
3. Update the agent instructions if needed

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Include docstrings for all functions
- Add logging for important operations

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

1. **404 Not Found Error**
   - Check your Ghost API URL format
   - Verify your deployment name in Azure OpenAI

2. **Authentication Failed**
   - Verify your API keys in `.env`
   - Check Ghost API key permissions

3. **Content Generation Issues**
   - Ensure Azure OpenAI service is properly configured
   - Check the model deployment name

### Getting Help

- Open an issue for bugs
- Check the Ghost API documentation
- Review Azure OpenAI service status

## 📚 Additional Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
- [Ghost API Documentation](https://ghost.org/docs/content-api/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/services/cognitive-services/openai-service/)

## ✨ Acknowledgments

- Microsoft Semantic Kernel team
- Ghost platform developers
- Azure OpenAI team
