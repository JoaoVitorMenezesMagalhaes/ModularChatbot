# Modular Chatbot with Router

A production-ready modular chatbot system that intelligently routes user messages to specialized agents with a modern React frontend, Redis-backed conversation management, and Kubernetes deployment.

## 🏗️ Architecture

### Backend Services
- **🔀 RouterAgent**: Intelligent message routing with LLM-based decision making
- **📚 KnowledgeAgent**: RAG-powered responses using Infinitepay documentation  
- **🧮 MathAgent**: Advanced mathematical expression processing
- **💾 Redis Service**: Conversation history and structured logging
- **🔄 Conversation Service**: Workflow orchestration and personality injection
- **🛡️ Security Layer**: Input sanitization, prompt injection prevention, and secure error handling

### Frontend
- **⚛️ React Application**: Modern chat interface with conversation management
- **🎨 Styled Components**: Beautiful, responsive UI design
- **📱 Real-time Chat**: Live conversation updates and agent workflow visualization

### Infrastructure
- **🐳 Docker**: Containerized applications for consistent deployment
- **☸️ Kubernetes**: Production-ready orchestration with auto-scaling
- **🔴 Redis**: High-performance data storage and caching
- **🌐 Nginx**: Load balancing and reverse proxy

## ✨ Features

- **Intelligent Routing**: LLM-powered decision making with confidence scoring
- **RAG Integration**: Retrieval-Augmented Generation for knowledge queries
- **Mathematical Processing**: Advanced math expression interpretation and solving
- **Conversation Management**: Multi-conversation support with Redis persistence
- **Agent Workflow Visualization**: Real-time display of agent decision process
- **Personality Injection**: Contextual responses with appropriate tone
- **Structured Logging**: Comprehensive logging with execution metrics
- **Security**: Input sanitization, prompt injection prevention, rate limiting
- **Production Ready**: Docker, Kubernetes, health checks, and monitoring

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API Key
- Node.js 18+ (for local development)

### Local Development with Docker Compose

1. **Clone and setup**:
```bash
git clone <repository-url>
cd ModularChatbotwithRouter
```

2. **Configure environment**:
```bash
# Create .env file
echo OPENAI_API_KEY="your_openai_api_key_here" > .env
```

3. **Start all services**:
```bash
docker-compose up --build
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Kubernetes Deployment

1. **Build and push images**:
```bash
# Build backend
docker build -t modular-chatbot-backend:latest .

# Build frontend
docker build -t modular-chatbot-frontend:latest ./frontend
```

2. **Update secrets**:
```bash
# Update k8s/secrets.yaml with your base64 encoded OpenAI API key
echo -n "your_openai_api_key_here" | base64
```

3. **Deploy to Kubernetes**:
```bash
kubectl apply -k k8s/
```

4. **Access via Ingress**:
- Add `127.0.0.1 chatbot.local` to your hosts file
- Access: http://chatbot.local

## 🧪 Running Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
python run_tests.py
```

### Run Unit Tests Only
```bash
python run_tests.py unit
```

### Run E2E Tests Only
```bash
python run_tests.py e2e
```

### Run Tests with Pytest Directly
```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/test_router_agent.py tests/test_math_agent.py -v

# E2E tests only
pytest tests/test_e2e_chat_api.py -v
```

## 📡 API Endpoints

### Chat Endpoints
- **POST** `/chat` - Main chat endpoint with intelligent routing
- **GET** `/conversations/{conversation_id}` - Get conversation history
- **GET** `/conversations/user/{user_id}` - Get user's conversations

### Utility Endpoints
- **GET** `/` - API information
- **GET** `/health` - Health check with service status
- **GET** `/docs` - Interactive API documentation

### API Request/Response Format

**Request**:
```json
{
  "message": "Qual a taxa da maquininha?",
  "user_id": "client789",
  "conversation_id": "conv-1234"
}
```

**Response**:
```json
{
  "response": "Olá! Aqui está a resposta com personalidade. 😊",
  "source_agent_response": "Texto gerado pelo agente especializado",
  "agent_workflow": [
    { "agent": "RouterAgent", "decision": "KnowledgeAgent" },
    { "agent": "KnowledgeAgent" }
  ],
  "conversation_id": "conv-1234",
  "timestamp": "2024-01-01T12:00:00Z",
  "user_id": "client789"
}

## Usage Examples

### Mathematical Queries
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How much is 65 x 3.11?"}'
```

### Knowledge Queries
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I integrate with Infinitepay API?"}'
```

## 🏗️ Detailed Architecture

### Router Agent
The RouterAgent intelligently decides which specialized agent should handle each user message:
- **LLM-based Decision**: Uses OpenAI to analyze message content and context
- **Confidence Scoring**: Provides confidence levels for routing decisions
- **Fallback Logic**: Rule-based fallback when LLM is unavailable
- **Security Integration**: Validates input and detects prompt injection attempts

### Knowledge Agent
The KnowledgeAgent provides RAG-powered responses using Infinitepay documentation:
- **Document Scraping**: Automatically scrapes content from Infinitepay docs
- **Vector Storage**: Uses FAISS for efficient similarity search
- **Source Tracking**: Logs sources of information for transparency
- **Context-Aware**: Maintains conversation context for better responses

### Math Agent
The MathAgent handles mathematical expressions and calculations:
- **Expression Parsing**: Intelligently extracts math from natural language
- **Safe Evaluation**: Secure mathematical expression evaluation
- **Step-by-Step Explanations**: Uses LLM for detailed explanations
- **Error Handling**: Graceful handling of invalid expressions

### Redis Integration
Redis provides high-performance data storage and caching:
- **Conversation History**: Persistent storage of all conversations
- **Structured Logging**: Centralized logging with metadata
- **Data Expiration**: Automatic cleanup of old data
- **Health Monitoring**: Connection health checks

### Security Layer
Comprehensive security measures protect the system:
- **Input Sanitization**: Removes malicious HTML, JS, and SQL injection attempts
- **Prompt Injection Prevention**: Detects and blocks manipulation attempts
- **Rate Limiting**: Prevents DoS attacks with per-IP limits
- **Secure Error Handling**: Never exposes system details to clients

## 🎨 Frontend Access and Testing

### Accessing the Frontend
1. **Start the system**: `docker-compose up --build`
2. **Open browser**: Navigate to http://localhost:3000
3. **Create conversation**: Click "Nova Conversa" to start
4. **Test multiple conversations**: Use the sidebar to switch between conversations

### Testing Multiple Conversations
- **New Conversation**: Each conversation gets a unique ID
- **Conversation History**: All messages are persisted in Redis
- **User Tracking**: Each user can have multiple conversations
- **Agent Workflow**: See which agents processed each message

### Frontend Features
- **Real-time Chat**: Live updates as you type and send messages
- **Agent Visualization**: See which agents processed each response
- **Conversation Management**: Easy switching between conversations
- **Responsive Design**: Works on desktop and mobile devices

## 📊 Example Logs (JSON Format)

### Router Agent Decision Log
```json
{
  "timestamp": "2025-01-07T14:32:12Z",
  "level": "INFO",
  "agent": "RouterAgent",
  "conversation_id": "conv-1234",
  "user_id": "client789",
  "execution_time": 0.245,
  "decision": "KnowledgeAgent",
  "confidence": 0.85,
  "reasoning": "User asked about Infinitepay API integration",
  "processed_content": "Como faço para integrar com a API do Infinitepay?",
  "metadata": {"routing_method": "llm"}
}
```

### Knowledge Agent Execution Log
```json
{
  "timestamp": "2025-01-07T14:32:15Z",
  "level": "INFO",
  "agent": "KnowledgeAgent",
  "conversation_id": "conv-1234",
  "user_id": "client789",
  "execution_time": 1.234,
  "processed_content": "Para integrar com a API do Infinitepay...",
  "metadata": {
    "sources_count": 3,
    "sources": ["https://ajuda.infinitepay.io/..."],
    "rag_system_available": true
  }
}
```

### Math Agent Execution Log
```json
{
  "timestamp": "2025-01-07T14:32:18Z",
  "level": "INFO",
  "agent": "MathAgent",
  "conversation_id": "conv-5678",
  "user_id": "client456",
  "execution_time": 0.567,
  "processed_content": "Expression: 65 * 3.11, Result: 202.15",
  "metadata": {
    "expression": "65 * 3.11",
    "result": 202.15,
    "calculation_successful": true
  }
}
```

### Security Event Log
```json
{
  "timestamp": "2025-01-07T14:32:25Z",
  "level": "INFO",
  "agent": "System",
  "conversation_id": "conv-9999",
  "user_id": "suspicious_user",
  "execution_time": 0.012,
  "message": "Prompt injection attempt blocked",
  "metadata": {
    "confidence": 0.92,
    "patterns_found": ["ignore previous instructions"],
    "client_ip": "192.168.1.100",
    "security_action": "blocked"
  }
}
```

## 🛡️ Security Features

### Input Sanitization
The system automatically sanitizes all user inputs to prevent malicious content:
- **HTML/JS Removal**: Strips `<script>`, `<iframe>`, and other dangerous tags
- **SQL Injection Prevention**: Blocks common SQL injection patterns
- **Command Injection Protection**: Prevents shell command execution
- **XSS Protection**: HTML escaping and content validation

### Prompt Injection Prevention
Advanced detection and blocking of prompt injection attempts:
- **Pattern Detection**: Identifies common injection patterns
- **Confidence Scoring**: Risk assessment based on pattern matches
- **Secure Prompts**: Dynamic security instructions based on threat level
- **Agent-Specific Protection**: Each agent validates input independently

### Rate Limiting
Protection against DoS attacks and abuse:
- **Per-IP Limits**: 60 requests per minute per IP address
- **Automatic Cleanup**: Old rate limit data is automatically removed
- **Graceful Degradation**: System continues to function under load
- **Monitoring**: Rate limit events are logged for analysis

## 📁 Project Structure

```
ModularChatbotwithRouter/
├── agents/                    # Specialized AI agents
│   ├── __init__.py
│   ├── router_agent.py        # Intelligent message routing
│   ├── knowledge_agent.py     # RAG-powered knowledge agent
│   └── math_agent.py          # Mathematical processing agent
├── services/                  # Business logic services
│   ├── __init__.py
│   ├── redis_service.py       # Redis conversation management
│   └── conversation_service.py # Workflow orchestration
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── logger.py              # Structured logging
│   ├── security.py            # Security utilities
│   └── error_handler.py       # Error handling
├── middleware/                # Security middleware
│   ├── __init__.py
│   └── security_middleware.py # Input validation and rate limiting
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_router_agent.py   # Router agent unit tests
│   ├── test_math_agent.py     # Math agent unit tests
│   └── test_e2e_chat_api.py   # E2E API tests
├── examples/                  # Example code and logs
│   ├── __init__.py
│   └── logging_examples.py    # Structured logging examples
├── frontend/                  # React application
│   ├── public/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── k8s/                       # Kubernetes manifests
│   ├── namespace.yaml
│   ├── redis-deployment.yaml
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   ├── secrets.yaml
│   └── kustomization.yaml
├── models.py                  # Pydantic data models
├── config.py                  # Configuration settings
├── main.py                    # FastAPI application
├── Dockerfile                 # Backend container
├── docker-compose.yml         # Local development
├── requirements.txt           # Python dependencies
├── pytest.ini                # Test configuration
├── run_tests.py              # Test runner script
└── README.md                  # This file
```

## Configuration

The application can be configured through environment variables:

- `OPENAI_API_KEY`: Required. Your OpenAI API key for LLM access
- `LOG_LEVEL`: Optional. Logging level (default: INFO)

## Development

The project follows clean architecture principles:

- **Separation of Concerns**: Each agent has a single responsibility
- **Dependency Injection**: Configuration and dependencies are injected
- **Error Handling**: Comprehensive error handling with logging
- **Type Safety**: Full type hints with Pydantic models
- **Testing**: Structured for easy unit testing

## Logging

The system provides structured logging with:

- Agent decision details
- Execution times
- Source information for knowledge queries
- Error tracking and debugging information

Logs are formatted as JSON for easy parsing and analysis.

## License

This project is licensed under the MIT License.
