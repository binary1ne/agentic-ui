# Enterprise Flask + Angular Microservice Backend

A headless Flask-based microservice with JWT authentication, LangChain Agentic RAG, LangGraph tool calling, and guardrails middleware.

## Features

- **User Management**: JWT-based authentication with role-based access control (User, Admin)
- **LangChain Agentic RAG**: Document upload and chat with Google Gemini + Chroma vector database
- **LangGraph Tool Calling**: AI chat with web search, API calls, and calculator tools
- **Guardrails Middleware**: Content moderation with PII detection, profanity filter, and custom rules
- **Component Management**: Dynamic component access control per role

## Tech Stack

- **Framework**: Flask 3.0 with flask-smorest (OpenAPI/Swagger)
- **Database**: SQLAlchemy with SQLite
- **Authentication**: JWT (Flask-JWT-Extended)
- **AI/ML**: LangChain, LangGraph, Google Gemini 2.0 Flash
- **Vector Storage**: Chroma + FAISS embeddings

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration
├── models.py               # Database models
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── services/              # Business logic layer
│   ├── auth_service.py
│   ├── user_service.py
│   ├── component_service.py
│   ├── rag_service.py
│   ├── chat_service.py
│   └── guardrails_service.py
└── controllers/           # API endpoints
    ├── auth_controller.py
    ├── user_controller.py
    ├── rag_controller.py
    ├── chat_controller.py
    ├── component_controller.py
    └── guardrails_controller.py
```

## Setup Instructions

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your-actual-google-gemini-api-key
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-random-jwt-secret
```

### 4. Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 5. Access API Documentation

Visit `http://localhost:5000/swagger-ui` for interactive API documentation.

## Default Credentials

- **Email**: admin@example.com
- **Password**: Admin@123
- **Role**: admin

⚠️ **IMPORTANT**: Change these credentials immediately after first login!

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### User Management (Admin Only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}/role` - Update user role
- `DELETE /api/users/{id}` - Delete user

### RAG (Document Chat)
- `POST /api/rag/upload` - Upload document
- `POST /api/rag/chat` - Chat with documents
- `GET /api/rag/documents` - List documents
- `DELETE /api/rag/documents/{id}` - Delete document

### Tool Calling Chat
- `POST /api/chat/tool-calling` - Chat with tools
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### Component Management
- `GET /api/components` - List available components
- `GET /api/components/user` - Get user's components
- `POST /api/components/assign` - Assign component to role (Admin)
- `GET /api/components/role/{role}` - Get role's components (Admin)

### Guardrails
- `GET /api/guardrails/config` - Get guardrails config
- `POST /api/guardrails/config` - Create guardrail rule (Admin)
- `PUT /api/guardrails/config/{id}` - Update guardrail (Admin)
- `DELETE /api/guardrails/config/{id}` - Delete guardrail (Admin)
- `GET /api/guardrails/logs` - Get detection logs (Admin)

## Usage Examples

### Login and Get Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin@123"}'
```

### Upload Document

```bash
curl -X POST http://localhost:5000/api/rag/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.pdf"
```

### Chat with Documents

```bash
curl -X POST http://localhost:5000/api/rag/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?","use_internet":false}'
```

### Tool Calling Chat

```bash
curl -X POST http://localhost:5000/api/chat/tool-calling \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Search the web for latest AI news"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | Flask secret key | Change in production |
| `JWT_SECRET_KEY` | JWT signing key | Change in production |
| `DATABASE_URI` | Database connection string | sqlite:///app.db |
| `GUARDRAILS_ENABLED` | Enable/disable guardrails | True |
| `CHROMA_DB_PATH` | Chroma vector DB path | ./data/chroma |
| `DOCUMENTS_PATH` | Uploaded documents path | ./data/documents |

## Security Notes

1. **Change default admin credentials** immediately
2. **Use strong SECRET_KEY and JWT_SECRET_KEY** in production
3. **Enable HTTPS** in production deployment
4. **Configure CORS** properly for your frontend domain
5. **Set appropriate file size limits** for uploads
6. **Keep API keys secure** and never commit to version control

## Troubleshooting

### Import Errors
Make sure virtual environment is activated and dependencies are installed.

### Database Errors
Delete `app.db` and restart to recreate database.

### API Key Errors
Verify `GOOGLE_API_KEY` is set correctly in `.env` file.

### Chroma/FAISS Errors
Ensure sufficient disk space for vector databases.

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

## License

Enterprise-grade application for internal use.
