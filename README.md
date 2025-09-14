# 🎓 Multi-Agent System Advisor

An advanced AI-powered analysis system that leverages the OODA (Observe, Orient, Decide, Act) loop methodology to provide comprehensive technical insights through a multi-agent architecture. This system specializes in distributed systems, consensus algorithms, and performance analysis for complex technical questions.

## 🌟 Features

- **Multi-Agent Architecture**: Utilizes specialized AI professors (Algorithms, Systems, Security, Finance) for domain-specific analysis
- **OODA Loop Methodology**: Implements military-grade decision-making framework for systematic problem-solving
- **Modern Web Interface**: Beautiful, responsive UI with real-time analysis and interactive features
- **Evidence-Based Analysis**: Provides citations and confidence scores for all insights
- **Performance Metrics**: Tracks token usage, execution time, and system performance
- **Fallback Mechanisms**: Robust error handling with graceful degradation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Ollama (for LLM integration)
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd multi-agent-system-advisor
   ```

2. **Set up the virtual environment**
   ```bash
   cd my_api_server
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama (Optional but recommended)**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama serve &
   ollama pull llama3
   ```

### Running the Application

1. **Start the Flask server**
   ```bash
   cd my_api_server
   source venv/bin/activate
   python src/main.py
   ```

2. **Access the web interface**
   Open your browser and navigate to `http://localhost:5000`

3. **Start analyzing!**
   Enter your technical question and click "Analyze Question"

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Frontend)                 │
├─────────────────────────────────────────────────────────────┤
│                    Flask API Server                        │
├─────────────────────────────────────────────────────────────┤
│                    OODA Loop Engine                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │Prof.        │ │Prof.        │ │Prof.        │ │Prof.    │ │
│  │Algorithms   │ │Systems      │ │Security     │ │Finance  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│                Knowledge Base & MCP Server                  │
├─────────────────────────────────────────────────────────────┤
│                    Ollama LLM Integration                   │
└─────────────────────────────────────────────────────────────┘
```

### OODA Loop Implementation

1. **Observe**: Question analysis and context gathering
2. **Orient**: Strategic planning and decomposition into sub-questions
3. **Decide**: Evidence gathering through professor consultation
4. **Act**: Synthesis and validation of final analysis

### Multi-Agent Professors

- **Prof. Algorithms**: Specializes in consensus algorithms, distributed systems
- **Prof. Systems**: Focuses on performance, latency, and system architecture
- **Prof. Security**: Expert in Byzantine fault tolerance and security
- **Prof. Finance**: Analyzes financial systems and trading requirements

## 🎯 Usage Examples

### Example Questions

1. **Consensus Algorithms**
   ```
   Compare Raft vs PBFT consensus algorithms for financial trading systems with sub-100ms latency requirements
   ```

2. **Multi-Agent Systems**
   ```
   How do multi-agent systems handle Byzantine fault tolerance in distributed environments?
   ```

3. **Performance Analysis**
   ```
   What are the performance implications of consensus algorithms in high-frequency trading?
   ```

### API Usage

The system provides a REST API endpoint for programmatic access:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "Your technical question here"}'
```

Response format:
```json
{
  "analysis": "• Insight 1 [1]\n• Insight 2 [2]\n• Insight 3 [3]\nDONE",
  "metrics": "Duration: 2.34s | Tools: {'search': 3, 'vector': 6} | Errors: 0",
  "log": ["[0.12s] 🎯 OBSERVE: Question received...", "..."]
}
```

## 🛠️ Configuration

### Environment Variables

- `MODEL`: Ollama model to use (default: "llama3:latest")
- `OLLAMA_URL`: Ollama API endpoint (default: "http://localhost:11434/api/generate")

### Customization

The system can be extended by:

1. **Adding new professors**: Create new classes inheriting from `ProfessorBase`
2. **Expanding knowledge base**: Add entries to the `SimpleMCPServer.kb` array
3. **Modifying UI**: Edit `src/static/index.html` for interface changes

## 📁 Project Structure

```
my_api_server/
├── src/
│   ├── main.py              # Flask application entry point
│   ├── advisor_logic.py     # Core OODA loop and multi-agent logic
│   ├── static/
│   │   └── index.html       # Web interface
│   ├── models/              # Database models (unused in current version)
│   └── routes/              # Additional API routes (unused)
├── venv/                    # Python virtual environment
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧪 Testing

### Manual Testing

1. Start the application
2. Navigate to the web interface
3. Try the example questions provided
4. Verify that results are displayed correctly

### API Testing

```bash
# Test the analyze endpoint
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 🚀 Deployment

### Local Development

The application is configured to run on `0.0.0.0:5000` for local development and testing.

### Production Deployment

For production deployment:

1. Set `debug=False` in `main.py`
2. Use a production WSGI server like Gunicorn
3. Configure environment variables appropriately
4. Set up proper logging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask and modern web technologies
- Powered by Ollama for local LLM inference
- Inspired by military OODA loop decision-making methodology
- Designed for technical analysis and research applications

## 📞 Support

For questions, issues, or contributions, please:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Follow the contribution guidelines

---

**Built with ❤️ for the technical community**

