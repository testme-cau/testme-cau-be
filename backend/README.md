# test.me Backend API 📚

> AI-powered exam generation and grading system backend that analyzes lecture PDFs using GPT-5 or Gemini

## Overview

**test.me** is a FastAPI-based REST API that powers an AI-driven learning platform. Users upload university lecture PDFs, and AI services (GPT-5 or Gemini) generate customized exam questions. The system then automatically grades student submissions and provides feedback.

### Core Concept

1. User authenticates via Firebase OAuth 2.0 (Android app)
2. User uploads a lecture PDF via Android app
3. PDF is uploaded to selected AI service (GPT or Gemini)
4. AI directly reads and analyzes the PDF (including text, images, tables)
5. AI generates customized exam questions
6. User submits answers
7. AI grades the answers by referencing the original PDF and provides feedback

### AI Provider Selection

The system supports **multiple AI providers** with a unified interface:
- **GPT-5** (OpenAI) - Default provider with model fallback
- **Gemini 1.5 Pro** (Google) - Alternative provider

Users can select the AI provider via query parameter or use the system default.

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn (ASGI)
- **Authentication**: Firebase OAuth 2.0 (with Firebase Admin SDK)
- **Database**: Cloud Firestore (NoSQL document database)
- **Storage**: Firebase Cloud Storage (PDF file storage with signed URLs)
- **AI Integration**: 
  - OpenAI GPT-5 API (Assistants API with file_search)
  - Google Generative AI (Gemini 1.5 Pro)
- **Data Validation**: Pydantic 2.5+
- **Testing**: pytest with async support
- **Python**: 3.11+

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Firebase project with Authentication, Firestore, and Storage enabled
- OpenAI API key (for GPT)
- Google AI API key (for Gemini, optional)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd be
```

2. **Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```env
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Server Configuration
HOST=0.0.0.0
PORT=5000

# File Upload
MAX_FILE_SIZE=16777216

# Firebase
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json

# AI Services
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-5

# Optional: Google AI (Gemini)
GOOGLE_API_KEY=your-google-ai-key
GOOGLE_MODEL=gemini-1.5-pro

# AI Provider Selection
DEFAULT_AI_PROVIDER=gpt  # or gemini

# CORS
CORS_ORIGINS=*
```

5. **Set up Firebase credentials**

Download your Firebase service account key JSON file from Firebase Console and save it as `serviceAccountKey.json` in the project root (this file is ignored by git).

6. **Run the development server**

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 5000

# Or using the main.py script
python main.py
```

The API will be available at `http://localhost:5000`

**Interactive API Documentation**:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Project Structure

```
be/
├── main.py                 # FastAPI application entry point
├── config.py              # Pydantic Settings configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment variables template
├── serviceAccountKey.json # Firebase credentials (not in git)
│
├── app/                   # Main application package
│   ├── __init__.py
│   │
│   ├── models/           # Pydantic models
│   │   ├── domain.py     # Domain models (User, PDF, Exam)
│   │   ├── requests.py   # Request schemas
│   │   └── responses.py  # Response schemas
│   │
│   ├── dependencies/     # FastAPI dependencies
│   │   ├── auth.py       # Authentication
│   │   └── ai_service.py # AI service injection
│   │
│   ├── routes/           # API routers
│   │   ├── main.py       # Health check endpoints
│   │   ├── pdf.py        # PDF management
│   │   └── exam.py       # Exam generation/grading
│   │
│   ├── services/         # Business logic
│   │   ├── ai_service_interface.py  # Abstract AI interface
│   │   ├── ai_factory.py            # AI service factory
│   │   ├── gpt_service.py           # GPT implementation
│   │   ├── gemini_service.py        # Gemini implementation
│   │   └── firebase_storage.py      # Storage service
│   │
│   └── utils/            # Utility functions
│
└── tests/                # pytest test suite
    ├── conftest.py       # Test fixtures
    ├── test_auth.py      # Authentication tests
    ├── test_main.py      # Main API tests
    ├── test_pdf_routes.py  # PDF API tests
    └── test_exam_routes.py # Exam API tests
```

## API Endpoints

### Authentication

All API endpoints (except `/`, `/health`, `/api/health`) require a Firebase ID token in the `Authorization` header:

```
Authorization: Bearer <firebase-id-token>
```

### Main Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /api/health` - API health check

### PDF Management

- `POST /api/pdf/upload` - Upload PDF file
- `GET /api/pdf/{file_id}/download` - Download PDF (signed URL)
- `GET /api/pdf/list` - List user's PDFs
- `DELETE /api/pdf/{file_id}` - Delete PDF

### Exam Management

- `POST /api/exam/generate?ai_provider=gpt` - Generate exam (choose AI provider)
- `GET /api/exam/{exam_id}` - Get exam details
- `GET /api/exam/list` - List user's exams

### API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## AI Provider Selection

### Using Query Parameters

Select AI provider when generating exams:

```bash
# Use GPT
curl -X POST "http://localhost:5000/api/exam/generate?ai_provider=gpt" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"pdf_id": "...", "num_questions": 10, "difficulty": "medium"}'

# Use Gemini
curl -X POST "http://localhost:5000/api/exam/generate?ai_provider=gemini" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"pdf_id": "...", "num_questions": 10, "difficulty": "medium"}'
```

### Setting Default Provider

Configure the default AI provider in `.env`:

```env
DEFAULT_AI_PROVIDER=gpt  # or gemini
```

If no query parameter is provided, the system uses the default provider.

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_pdf_routes.py -v

# Run async tests
pytest tests/test_auth.py -v -s
```

### Test Structure

- `tests/conftest.py` - Shared fixtures
- `tests/test_*.py` - Test modules
- Uses `TestClient` for API testing
- Mocks external services (Firebase, AI providers)

## Development

### Code Style

- Follow PEP 8 style guide
- Use type hints throughout
- Write docstrings for all functions
- Use Pydantic models for data validation

### Adding New Features

1. **Define Pydantic Models** (if needed)
2. **Create Route Handler** with proper dependencies
3. **Write Tests** (TDD approach)
4. **Update Documentation**

### FastAPI Features Used

- **Dependency Injection**: `Depends()` for reusable components
- **Automatic Validation**: Pydantic models
- **Interactive Docs**: Swagger UI and ReDoc
- **Async Support**: For I/O-bound operations
- **Response Models**: Type-safe responses

## Deployment

### Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with multiple workers
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```

### Environment Considerations

- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Enable HTTPS only
- Configure proper CORS origins
- Set up logging and monitoring
- Use environment-specific `.env` files

## Architecture Highlights

### Strategy Pattern for AI Services

The system uses the **Strategy Pattern** to abstract AI providers:

```python
# All AI providers implement the same interface
class AIServiceInterface(ABC):
    def generate_exam_from_pdf(...)
    def grade_exam_with_pdf(...)
    def grade_answer(...)
    
# Concrete implementations
class GPTService(AIServiceInterface): ...
class GeminiService(AIServiceInterface): ...

# Factory pattern for provider selection
def get_ai_service(provider: str) -> AIServiceInterface:
    if provider == "gpt":
        return GPTService()
    elif provider == "gemini":
        return GeminiService()
```

This design allows:
- Easy addition of new AI providers
- Seamless provider switching
- Consistent API regardless of provider
- Testability with mock providers

## Troubleshooting

### Firebase Issues

- Verify `serviceAccountKey.json` is valid
- Check Firebase project configuration
- Ensure all Firebase services are enabled

### AI Service Issues

**GPT**:
- Verify `OPENAI_API_KEY` is valid
- Check API usage limits and billing

**Gemini**:
- Verify `GOOGLE_API_KEY` is valid
- Check API quota and billing
- Ensure Gemini API is enabled in Google Cloud

### Common Errors

- **401 Unauthorized**: Invalid or expired Firebase token
- **400 Bad Request**: Invalid request data (check Pydantic validation)
- **500 Internal Server Error**: Check logs for specific error

## Development Status

This project is in active development. Core features are implemented with FastAPI and support for multiple AI providers.

### Features

✅ FastAPI REST API  
✅ Firebase Authentication  
✅ PDF Upload/Management  
✅ Multi-provider AI Integration (GPT + Gemini)  
✅ Exam Generation  
✅ Automatic API Documentation  
✅ Comprehensive Testing  

## Contributing

See AGENTS.md for detailed technical documentation and development guidelines.

## License

This project is licensed under the MIT License.

---

**Framework**: FastAPI 0.109.0  
**AI Providers**: GPT-5, Gemini 1.5 Pro  
**Built with** ❤️ **for students**
