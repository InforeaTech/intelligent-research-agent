# Intelligent Research Agent

An advanced AI-powered research assistant that creates professional profiles and generates personalized LinkedIn connection notes using LLMs (Gemini/OpenAI).

## Features

- 🔍 **Deep Research**: Multi-step research with three modes (RAG, Tools, Hybrid)
- 🤖 **Autonomous Agents**: LLM-driven tool usage for complex queries
- 📊 **Profile Generation**: Automated professional profile creation
- 💬 **Note Generation**: Personalized LinkedIn connection request messages
- 💾 **Smart Caching**: 80% fuzzy matching with cache bypass option
- 🔐 **Secure Secrets**: Encrypted API key management
- 📝 **Comprehensive Logging**: SQLite-based interaction tracking
- 🏗️ **Microservices Ready**: Modular architecture for easy scaling

See [DEEP_RESEARCH.md](DEEP_RESEARCH.md) for detailed documentation on research capabilities.

## Architecture

- **Monolithic Backend** (`backend/`): Production-ready FastAPI application
- **Microservices** (`microservices_app/`): Decoupled service architecture (optional)

## Quick Start

### Prerequisites

- Python 3.8+
- API Keys (Gemini or OpenAI)
- Serper API Key (optional, for enhanced search)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/intelligent-research-agent.git
cd intelligent-research-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here (optional)
SERPER_API_KEY=your_serper_api_key_here (optional)
```

### Running the Application

**Monolithic Backend:**
```bash
cd backend
python main.py
```

**Microservices Architecture:**
```bash
python run_services.py
```

Access the API at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## API Endpoints

- `POST /api/research` - Generate professional profile
- `POST /api/generate-note` - Create LinkedIn connection note
- `POST /api/deep-research` - Perform comprehensive research
- `POST /api/secrets/set` - Store encrypted API key
- `GET /api/secrets/get/{key}` - Retrieve stored API key

## Key Technologies

- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Google Gemini** - Advanced LLM
- **OpenAI** - Alternative LLM provider
- **BeautifulSoup4** - Web scraping
- **SQLite** - Local database
- **Cryptography** - Secret encryption

## Project Structure

```
├── backend/              # Main application
│   ├── main.py          # FastAPI app & endpoints
│   ├── agent.py         # Orchestration layer
│   ├── schemas.py       # Pydantic models
│   ├── database.py      # SQLite manager
│   ├── search_service.py   # Search & scraping
│   ├── content_service.py  # LLM generation
│   └── secrets_manager.py  # Encrypted secrets
│
├── microservices_app/   # Microservices architecture
│   ├── gateway/         # API Gateway (Port 8000)
│   ├── search_service/  # Search service (Port 8001)
│   ├── content_service/ # Content service (Port 8002)
│   └── audit_service/   # Logging service (Port 8003)
│
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

## Advanced Features

### Fuzzy Caching

The system intelligently caches results:
- **80% similarity matching** for text inputs
- **Exact matching** for tone/length parameters
- **Bypass option** via `bypass_cache` flag

### Database Logging

All interactions are logged to `agent_logs.db`:
- User inputs
- Search results
- Model prompts and outputs
- Final results

## Security

- API keys stored encrypted using `cryptography.fernet`
- Master key auto-generated on first run
- Never commit `.env`, `master.key`, or `secrets.enc`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Google Gemini API
- OpenAI API
- Serper.dev for enhanced search

## Support

For issues and questions, please open a GitHub issue.
