# test.me Backend API - Agent Documentation 🤖

> Technical specification and architecture guide for AI agents working on the test.me backend

## Project Overview

**test.me** is a FastAPI-based REST API backend for an AI-powered exam generation and grading platform. The system processes university lecture PDFs using multiple AI providers (GPT-5, Gemini) to generate customized exam questions and automatically grade student submissions.

### System Architecture

```
User (Android App) → FastAPI API → Firebase (Auth/Storage/Firestore) → AI Services (GPT/Gemini)
```

### Core Workflow

1. **Authentication**: User authenticates via Firebase OAuth 2.0 (Android app) or admin login (web interface)
2. **Upload**: PDF uploaded to Firebase Cloud Storage
3. **Processing**: PDF uploaded to AI service via provider API
4. **Generation**: AI (GPT-5 or Gemini) directly reads PDF and generates exam questions
5. **Submission**: User submits answers via API
6. **Grading**: AI evaluates answers by referencing the original PDF and provides feedback
7. **Storage**: All metadata stored in Cloud Firestore

## Technology Stack

### Backend Framework

- **FastAPI 0.109.0**: Modern, fast web framework
- **Uvicorn 0.27.0**: ASGI server
- **Pydantic 2.5.3**: Data validation and settings management
- **Python 3.11+**: Minimum Python version

### Firebase Services

- **firebase-admin 6.5.0**: Python Admin SDK
  - **Authentication**: ID token verification
  - **Cloud Storage**: PDF file storage with signed URLs
  - **Cloud Firestore**: NoSQL document database

### AI Integration

- **openai >=1.0.0**: OpenAI Python library
- **google-generativeai 0.3.2**: Google Generative AI SDK
- **Supported AI Providers**:
  - **GPT**: GPT-5 (with fallback to gpt-4.1, gpt-4o, gpt-4o-mini)
  - **Gemini**: Gemini 1.5 Pro/Flash
- **Use Cases**:
  - Direct PDF reading and exam question generation
  - PDF-referenced answer grading with detailed feedback
  - Provider selection via query parameter or environment default

### Utilities

- **python-dotenv 1.0.1**: Environment variable management
- **httpx 0.26.0**: Async HTTP client
- **pytest 7.4.3**: Testing framework
- **pytest-asyncio 0.23.3**: Async testing support

## Project Structure

```
be/
├── main.py                      # FastAPI application entry point
├── config.py                    # Pydantic Settings configuration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (gitignored)
├── .env.example                # Environment template
├── serviceAccountKey.json      # Firebase credentials (gitignored)
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── domain.py           # Domain models (User, PDF, Exam)
│   │   ├── requests.py         # Request schemas
│   │   └── responses.py        # Response schemas
│   │
│   ├── dependencies/           # FastAPI dependencies
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication dependency
│   │   └── ai_service.py       # AI service injection
│   │
│   ├── routes/                 # API routers
│   │   ├── __init__.py
│   │   ├── main.py             # Root and health endpoints
│   │   ├── pdf.py              # PDF upload/download/delete
│   │   └── exam.py             # Exam generation/grading
│   │
│   ├── services/               # Business logic
│   │   ├── ai_service_interface.py  # AI service abstract interface
│   │   ├── ai_factory.py            # AI service factory
│   │   ├── gpt_service.py           # OpenAI GPT implementation
│   │   ├── gemini_service.py        # Google Gemini implementation
│   │   └── firebase_storage.py      # Firebase Storage wrapper
│   │
│   ├── utils/                  # Utility functions
│   │   └── file_utils.py       # File validation helpers
│   │
│   ├── templates/              # HTML templates (admin page)
│   └── static/                 # Static files
│
└── tests/                      # pytest test suite
    ├── conftest.py             # pytest fixtures
    ├── test_auth.py            # Authentication tests
    ├── test_main.py            # Main API tests
    ├── test_pdf_routes.py      # PDF API tests
    ├── test_exam_routes.py     # Exam API tests
    ├── test_gpt_service.py     # GPT service tests
    └── test_gpt5_greeting.py   # GPT-5 connection test
```

## Configuration

### Environment Variables

| Variable                    | Required | Default                  | Description                                           |
| --------------------------- | -------- | ------------------------ | ----------------------------------------------------- |
| `SECRET_KEY`                | Yes      | -                        | FastAPI secret key (use `secrets.token_hex(32)`)      |
| `FLASK_ENV`                 | No       | `development`            | Environment mode (for compatibility)                  |
| `HOST`                      | No       | `0.0.0.0`                | Server host                                           |
| `PORT`                      | No       | `5000`                   | Server port                                           |
| `MAX_FILE_SIZE`             | No       | `16777216`               | Max upload size in bytes (16MB)                       |
| `FIREBASE_STORAGE_BUCKET`   | Yes      | -                        | Firebase storage bucket (e.g., `project.appspot.com`) |
| `FIREBASE_CREDENTIALS_PATH` | No       | `serviceAccountKey.json` | Path to Firebase service account key                  |
| `OPENAI_API_KEY`            | Yes      | -                        | OpenAI API key                                        |
| `OPENAI_MODEL`              | No       | `gpt-5`                  | OpenAI model name                                     |
| `GOOGLE_API_KEY`            | No       | -                        | Google AI API key (for Gemini)                        |
| `GOOGLE_MODEL`              | No       | `gemini-1.5-pro`         | Gemini model name                                     |
| `DEFAULT_AI_PROVIDER`       | No       | `gpt`                    | Default AI provider: gpt or gemini                    |
| `CORS_ORIGINS`              | No       | `*`                      | Comma-separated CORS origins                          |

### Firebase Setup

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com)
2. Enable **Authentication** (Email/Password, Google, etc.)
3. Create a **Cloud Firestore** database
4. Enable **Cloud Storage**
5. Generate a service account key:
   - Project Settings → Service Accounts → Generate New Private Key
   - Save as `serviceAccountKey.json` in project root

## API Endpoints

### Authentication

All API endpoints (except `/`, `/health`, `/api/health`) require Firebase ID token in the `Authorization` header:

```
Authorization: Bearer <firebase-id-token>
```

The `get_current_user` dependency verifies the token and injects user data into the route handler.

### Main Endpoints

#### `GET /`

Welcome message and API information

#### `GET /health`

Health check endpoint

#### `GET /api/health`

API health check endpoint

### PDF Management

#### `POST /api/pdf/upload`

Upload PDF to Firebase Storage

**Request**: `multipart/form-data` with `file` field  
**Response**: `PDFUploadResponse` with file information

#### `GET /api/pdf/{file_id}/download`

Get PDF download URL (redirects to Firebase signed URL, 1-hour expiration)

#### `GET /api/pdf/list`

List all PDFs for authenticated user

**Response**: `PDFListResponse` with list of PDFs

#### `DELETE /api/pdf/{file_id}`

Delete PDF from Firebase Storage and Firestore

### Exam Management

#### `POST /api/exam/generate?ai_provider=gpt`

Generate exam from uploaded PDF

**Query Parameters**:

- `ai_provider` (optional): `gpt` or `gemini` - defaults to `DEFAULT_AI_PROVIDER`

**Request Body** (`ExamGenerationRequest`):

```json
{
  "pdf_id": "uuid",
  "num_questions": 10,
  "difficulty": "medium"
}
```

**Response** (`ExamResponse`): Exam with questions, total points, estimated time, and AI provider used

#### `GET /api/exam/{exam_id}`

Get exam details

#### `GET /api/exam/list`

List all exams for authenticated user

**Response** (`ExamListResponse`): List of exams with metadata

## AI Service Architecture

### Strategy Pattern Implementation

The system uses the **Strategy Pattern** to abstract AI providers, allowing seamless switching between GPT and Gemini.

### Components

#### 1. AIServiceInterface (Abstract Base Class)

```python
from abc import ABC, abstractmethod

class AIServiceInterface(ABC):
    @abstractmethod
    def generate_exam_from_pdf(pdf_bytes, filename, num_questions, difficulty) -> Dict

    @abstractmethod
    def grade_exam_with_pdf(pdf_bytes, filename, questions, answers) -> Dict

    @abstractmethod
    def grade_answer(question, student_answer, correct_answer) -> Dict

    @property
    @abstractmethod
    def provider_name(self) -> str
```

#### 2. Concrete Implementations

- **GPTService**: Implements interface using OpenAI Assistants API
- **GeminiService**: Implements interface using Google Generative AI SDK

#### 3. AI Factory

```python
def get_ai_service(provider: Optional[str] = None) -> AIServiceInterface:
    """Factory function to get AI service instance"""
    provider = provider or settings.default_ai_provider
    if provider == "gpt":
        return GPTService()
    elif provider == "gemini":
        return GeminiService()
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

#### 4. FastAPI Dependency

```python
async def get_ai_service_dependency(
    ai_provider: Optional[str] = Query(None)
) -> AIServiceInterface:
    """Inject AI service based on query parameter or default"""
    return get_ai_service(ai_provider)
```

### Usage Example

```python
@router.post("/exam/generate")
async def generate_exam(
    request: ExamGenerationRequest,
    user: Dict = Depends(get_current_user),
    ai_service: AIServiceInterface = Depends(get_ai_service_dependency)
):
    # Use ai_service regardless of provider
    result = ai_service.generate_exam_from_pdf(...)
    provider_used = ai_service.provider_name  # "gpt" or "gemini"
    return ExamResponse(..., ai_provider=provider_used)
```

### Selecting AI Provider

**Via Query Parameter**:

```bash
POST /api/exam/generate?ai_provider=gemini
```

**Via Environment Variable**:

```env
DEFAULT_AI_PROVIDER=gemini
```

**Programmatically**:

```python
service = get_ai_service("gemini")
```

## Key Services

### GPTService (`app/services/gpt_service.py`)

Handles OpenAI API interactions using Assistants API for PDF processing.

**Key Methods**:

- `generate_exam_from_pdf(pdf_bytes, original_filename, num_questions, difficulty)`: Generate exam questions by uploading PDF to OpenAI
- `grade_exam_with_pdf(pdf_bytes, original_filename, questions, answers)`: Grade entire exam by referencing the original PDF
- `grade_answer(question, student_answer, correct_answer)`: Grade single answer without PDF reference

**Features**:

- **Assistants API**: Creates temporary assistant with file_search tool
- **Direct PDF Reading**: GPT reads PDF content including text, images, tables, and diagrams
- Model fallback: `gpt-5` → `gpt-4.1` → `gpt-4o` → `gpt-4o-mini`
- Automatic cleanup: Deletes uploaded files and assistants after use
- JSON response parsing with error handling

### GeminiService (`app/services/gemini_service.py`)

Handles Google Generative AI interactions for PDF processing.

**Key Methods**:

- `generate_exam_from_pdf(pdf_bytes, original_filename, num_questions, difficulty)`: Generate exam questions using Gemini
- `grade_exam_with_pdf(pdf_bytes, original_filename, questions, answers)`: Grade entire exam using Gemini
- `grade_answer(question, student_answer, correct_answer)`: Grade single answer

**Features**:

- **Gemini File API**: Uploads PDF for multimodal processing
- **Direct PDF Reading**: Gemini reads and analyzes PDF content
- Model: `gemini-1.5-pro` or `gemini-1.5-flash`
- Automatic cleanup: Deletes uploaded files after use
- JSON response parsing with markdown extraction

### FirebaseStorageService (`app/services/firebase_storage.py`)

Manages Firebase Cloud Storage operations.

**Key Methods**:

- `upload_file(file, user_id, original_filename)`: Upload PDF
- `get_download_url(storage_path, expiration)`: Generate signed URL
- `delete_file(storage_path)`: Delete file
- `download_file(storage_path)`: Download file as bytes

**Storage Path Format**: `pdfs/{user_id}/{uuid}.pdf`

## Data Models (Firestore)

### Users Collection: `users/{user_id}`

#### PDFs Subcollection: `users/{user_id}/pdfs/{file_id}`

```json
{
  "file_id": "uuid",
  "original_filename": "lecture.pdf",
  "unique_filename": "uuid.pdf",
  "storage_path": "pdfs/{user_id}/{uuid}.pdf",
  "size": 1024000,
  "user_id": "firebase_uid",
  "uploaded_at": "timestamp",
  "status": "uploaded"
}
```

#### Exams Subcollection: `users/{user_id}/exams/{exam_id}`

```json
{
  "exam_id": "firestore_auto_id",
  "pdf_id": "uuid",
  "user_id": "firebase_uid",
  "questions": [...],
  "total_points": 100,
  "estimated_time": 60,
  "num_questions": 10,
  "difficulty": "medium",
  "created_at": "timestamp",
  "status": "active",
  "ai_provider": "gpt"
}
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints throughout the codebase
- Document functions with detailed docstrings
- Keep functions focused and modular
- Use Pydantic models for data validation

### FastAPI Patterns

- **Dependencies**: Use `Depends()` for injection
- **Route Decorators**: `@router.get()`, `@router.post()`, etc.
- **Response Models**: Always specify `response_model`
- **Status Codes**: Use FastAPI status constants
- **Exceptions**: Raise `HTTPException` for errors

### Error Handling

- Use try-except blocks for external service calls
- Raise `HTTPException` with appropriate status codes
- Log errors using Python logging
- Return structured error responses
- Never expose internal error details to clients

### Security

- Never commit `.env` or `serviceAccountKey.json`
- Validate all user inputs with Pydantic models
- Use Firebase Admin SDK for token verification
- Generate signed URLs with short expiration times
- Implement rate limiting for production
- Use HTTPS only in production

### Testing

- Write tests before implementation (TDD)
- Use pytest with async support
- Mock external services (Firebase, OpenAI, Gemini)
- Test authentication and authorization
- Test error scenarios
- Run tests: `pytest tests/ -v`
- Check coverage: `pytest --cov=app tests/`

## Common Tasks

### Adding a New API Endpoint

1. **Define Pydantic Models** (if needed):

   - Request model in `app/models/requests.py`
   - Response model in `app/models/responses.py`

2. **Create Route Handler**:

   ```python
   from fastapi import APIRouter, Depends
   from app.dependencies.auth import get_current_user

   router = APIRouter()

   @router.post("/endpoint", response_model=MyResponse)
   async def my_endpoint(
       request: MyRequest,
       user: Dict = Depends(get_current_user)
   ):
       # Implementation
       return MyResponse(...)
   ```

3. **Register Router** in `main.py`:

   ```python
   app.include_router(my_router, prefix="/api/my")
   ```

4. **Write Tests** in `tests/test_my_routes.py`

### Adding a New AI Provider

1. **Create Service Class**:

   ```python
   from app.services.ai_service_interface import AIServiceInterface

   class MyAIService(AIServiceInterface):
       @property
       def provider_name(self) -> str:
           return "myai"

       def generate_exam_from_pdf(self, ...):
           # Implementation
           pass
   ```

2. **Update Factory** in `app/services/ai_factory.py`:

   ```python
   def get_ai_service(provider: Optional[str] = None):
       # ...
       elif provider == "myai":
           return MyAIService()
   ```

3. **Add Configuration** in `config.py`:

   ```python
   myai_api_key: str | None = Field(default=None)
   ```

4. **Write Tests**

### Modifying AI Behavior

Edit prompts in AI service classes:

- `GPTService.generate_exam_from_pdf()`: Modify instructions
- `GeminiService.generate_exam_from_pdf()`: Modify prompt

### Running the Application

**Development**:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

**Production**:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

**Using main.py**:

```bash
python main.py
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi.json

## Deployment Considerations

### Environment

- Set production environment variables
- Use strong `SECRET_KEY`
- Enable HTTPS only
- Set proper CORS origins
- Use environment-specific `.env` files

### FastAPI Deployment

- Use ASGI server (Uvicorn with multiple workers)
- Deploy behind reverse proxy (Nginx)
- Enable Gzip compression
- Set up logging and monitoring
- Use containerization (Docker)

### Firebase

- Use Firebase project with billing enabled
- Configure Storage security rules
- Set up Firestore indexes for queries
- Monitor usage and costs
- Set up proper IAM roles

### AI Services

- Monitor API usage and costs for both providers
- Implement caching for common requests
- Set usage limits and alerts
- Consider fallback strategies
- Track provider performance and accuracy

### Scaling

- Use multiple Uvicorn workers
- Implement job queue for long-running tasks
- Use Redis for caching
- Consider serverless deployment (Cloud Run)
- Horizontal scaling with load balancer

## Troubleshooting

### Firebase Initialization Failed

- Verify `serviceAccountKey.json` exists and is valid
- Check `FIREBASE_STORAGE_BUCKET` in `.env`
- Ensure Firebase project has required services enabled

### AI Service Errors

**GPT**:

- Verify `OPENAI_API_KEY` is valid
- Check API usage limits
- Review fallback model behavior in logs

**Gemini**:

- Verify `GOOGLE_API_KEY` is valid
- Check API quota and billing
- Ensure model name is correct

### PDF Upload/Processing Fails

- Check file size against `MAX_FILE_SIZE`
- Verify Firebase Storage permissions
- Ensure user is authenticated
- Check Firebase Storage rules
- Verify AI service can access PDFs

### Authentication Issues

- Verify Firebase ID token is being sent
- Check token hasn't expired
- Ensure Firebase project matches credentials
- Review Admin SDK initialization logs

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_pdf_routes.py -v

# Run with coverage
pytest --cov=app tests/

# Run async tests
pytest tests/test_auth.py -v -s
```

### Test Structure

- Use `pytest` fixtures for setup
- Mock external services
- Test both success and failure scenarios
- Use `TestClient` for API testing
- Test authentication and authorization

## License

MIT License - See LICENSE file for details

---

**For Human Developers**: See README.md for setup instructions  
**For AI Agents**: This document contains the complete technical specification

**Framework**: FastAPI 0.109.0  
**AI Providers**: GPT-5, Gemini 1.5 Pro  
**Architecture**: Strategy Pattern for AI abstraction

Last Updated: 2025-11-06
