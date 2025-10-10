# test.me Backend API - Agent Documentation 🤖

> Technical specification and architecture guide for AI agents working on the test.me backend

## Project Overview

**test.me** is a Flask-based REST API backend for an AI-powered exam generation and grading platform. The system processes university lecture PDFs using GPT-5 to generate customized exam questions and automatically grade student submissions.

### System Architecture

```
User (Android App) → Flask API → Firebase (Auth/Storage/Firestore) → OpenAI GPT-5
```

### Core Workflow

1. **Authentication**: User authenticates via Firebase OAuth 2.0 (Android app) or admin login (web interface)
2. **Upload**: PDF uploaded to Firebase Cloud Storage
3. **Processing**: PDF uploaded to OpenAI via Assistants API
4. **Generation**: GPT-5 directly reads PDF and generates exam questions
5. **Submission**: User submits answers via API
6. **Grading**: GPT-5 evaluates answers by referencing the original PDF and provides feedback
7. **Storage**: All metadata stored in Cloud Firestore

## Technology Stack

### Backend Framework

- **Flask 3.0.3**: Web framework
- **Werkzeug 3.0.3**: WSGI utilities
- **Flask-CORS 4.0.1**: Cross-origin resource sharing

### Firebase Services

- **firebase-admin 6.5.0**: Python Admin SDK
  - **Authentication**: ID token verification
  - **Cloud Storage**: PDF file storage with signed URLs
  - **Cloud Firestore**: NoSQL document database

### AI Integration

- **openai >=1.0.0**: OpenAI Python library
- **Model**: GPT-5 (with fallback to gpt-4.1, gpt-4o, gpt-4o-mini)
- **Assistants API**: For PDF file analysis with file_search tool
- **Use Cases**:
  - Direct PDF reading and exam question generation
  - PDF-referenced answer grading with detailed feedback

### Utilities

- **python-dotenv 1.0.1**: Environment variable management
- **requests 2.32.3**: HTTP requests
- **python-dateutil 2.9.0**: Date/time utilities

## Project Structure

```
be/
├── app.py                    # Application entry point
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
├── .env.example             # Environment template
├── serviceAccountKey.json   # Firebase credentials (gitignored)
│
├── app/
│   ├── __init__.py          # Flask app factory
│   │
│   ├── routes/              # API endpoints
│   │   ├── __init__.py      # Blueprint exports
│   │   ├── main.py          # Root and health endpoints
│   │   ├── admin.py         # Admin web interface
│   │   ├── api.py           # API blueprint and auth decorator
│   │   ├── pdf.py           # PDF upload/download/delete
│   │   └── exam.py          # Exam generation/grading
│   │
│   ├── services/            # Business logic
│   │   ├── gpt_service.py       # OpenAI GPT integration (Assistants API)
│   │   └── firebase_storage.py  # Firebase Storage wrapper
│   │
│   ├── utils/               # Utility functions
│   │   └── file_utils.py    # File validation helpers
│   │
│   ├── templates/           # HTML templates (admin page)
│   └── static/              # Static files
│
└── tests/                   # Test suite
    ├── test_gpt_service.py      # GPT service tests
    ├── test_gpt5_greeting.py    # GPT-5 basic test
    └── test_gpt5_verbose.py     # GPT-5 response analysis
```

## Configuration

### Environment Variables

| Variable                  | Required | Default       | Description                                           |
| ------------------------- | -------- | ------------- | ----------------------------------------------------- |
| `FLASK_APP`               | Yes      | `app.py`      | Flask application entry point                         |
| `FLASK_ENV`               | No       | `development` | Environment mode                                      |
| `SECRET_KEY`              | Yes      | -             | Flask secret key (use `secrets.token_hex(32)`)        |
| `HOST`                    | No       | `0.0.0.0`     | Server host                                           |
| `PORT`                    | No       | `5000`        | Server port                                           |
| `MAX_FILE_SIZE`           | No       | `16777216`    | Max upload size in bytes (16MB)                       |
| `FIREBASE_STORAGE_BUCKET` | Yes      | -             | Firebase storage bucket (e.g., `project.appspot.com`) |
| `OPENAI_API_KEY`          | Yes      | -             | OpenAI API key                                        |
| `OPENAI_MODEL`            | No       | `gpt-5`       | OpenAI model name                                     |
| `ADMIN_ID`                | No       | `admin`       | Admin page username (legacy)                          |
| `ADMIN_PW`                | No       | `admin`       | Admin page password (legacy)                          |

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

#### Firebase OAuth 2.0 (Android App Users)

All API endpoints (except `/` and `/health`) require Firebase ID token in the `Authorization` header:

```
Authorization: Bearer <firebase-id-token>
```

The `@require_firebase_auth` decorator verifies the token and adds `request.user` with Firebase user data.

#### Admin Login (Web Interface)

For development and testing purposes, an admin web interface is available at `/admin-page`:

- **Primary Login**: Google OAuth 2.0 via Firebase Web SDK
  - Real Firebase authentication tokens
  - Same flow as Android app users
  - Tokens stored in server-side session
  - Automatically included in API calls via session
- **Legacy Login**: Username/password with `ADMIN_ID` and `ADMIN_PW` (deprecated)
  - Creates mock Firebase user without real tokens
  - For backward compatibility only
  - Use OAuth for realistic testing
- **Purpose**: Web-based testing interface for API functionality without Android app
- **Security**: Only for development; requires proper Firebase configuration

**Note**: Admin OAuth login simulates the actual Android app authentication flow with real Firebase tokens.

### PDF Management

#### `POST /api/pdf/upload`

Upload PDF to Firebase Storage

**Request**: `multipart/form-data` with `file` field  
**Response**: `{ file_id, original_filename, file_url, uploaded_at, size }`

#### `GET /api/pdf/<file_id>/download`

Get PDF download URL (redirects to Firebase signed URL, 1-hour expiration)

#### `GET /api/pdf/list`

List all PDFs for authenticated user

#### `DELETE /api/pdf/<file_id>`

Delete PDF from Firebase Storage and Firestore

### Exam Management

#### `POST /api/exam/generate`

Generate exam from uploaded PDF

**Request Body**:

```json
{
  "pdf_id": "uuid",
  "num_questions": 10,
  "difficulty": "medium"
}
```

**Response**: Exam with questions, total points, estimated time

#### `GET /api/exam/<exam_id>`

Get exam details

#### `GET /api/exam/list`

List all exams for authenticated user

### Admin Interface

#### `GET /admin-page`

Web interface for testing with Google OAuth 2.0

**Authentication**:

- Primary: Google OAuth 2.0 via Firebase Web SDK (recommended)
- Legacy: Username/password with `ADMIN_ID` and `ADMIN_PW` (deprecated)

**Features**:

- Real Firebase Google authentication
- PDF upload and exam generation
- Full API testing with actual Firebase tokens
- Backend operation debugging
- User profile display with avatar and email

**Implementation**:

- Uses Firebase Web SDK (v10.7.1) from CDN
- Tokens stored in server-side session (HTTPOnly)
- Automatic token inclusion in API calls via `@require_firebase_auth` decorator
- Session verification on each API request

## Key Services

### GPTService (`app/services/gpt_service.py`)

Handles OpenAI API interactions using Assistants API for PDF processing.

**Key Methods**:

- `generate_exam_from_pdf(pdf_bytes, original_filename, num_questions, difficulty)`: Generate exam questions by uploading PDF to OpenAI
- `grade_exam_with_pdf(pdf_bytes, original_filename, questions, answers)`: Grade entire exam by referencing the original PDF
- `grade_answer(question, student_answer, correct_answer)`: Legacy method - Grade single answer without PDF reference

**Features**:

- **Assistants API**: Creates temporary assistant with file_search tool
- **Direct PDF Reading**: GPT reads PDF content including text, images, tables, and diagrams
- Model fallback: `gpt-5` → `gpt-4.1` → `gpt-4o` → `gpt-4o-mini`
- Automatic cleanup: Deletes uploaded files and assistants after use
- JSON response parsing with error handling

### FirebaseStorageService (`app/services/firebase_storage.py`)

Manages Firebase Cloud Storage operations.

**Key Methods**:

- `upload_file(file, user_id, original_filename)`: Upload PDF
- `get_download_url(storage_path, expiration)`: Generate signed URL
- `delete_file(storage_path)`: Delete file
- `download_file(storage_path)`: Download file as bytes

**Storage Path Format**: `pdfs/{user_id}/{uuid}.pdf`

**Note**: PDFs are temporarily downloaded from Firebase Storage and uploaded to OpenAI for processing, then cleaned up automatically.

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
  "status": "active"
}
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints where applicable
- Document functions with docstrings
- Keep functions focused and modular

### Error Handling

- Use try-except blocks for external service calls
- Log errors with `current_app.logger.error()`
- Return meaningful error messages to clients
- Use appropriate HTTP status codes

### Security

- Never commit `.env` or `serviceAccountKey.json`
- Validate all user inputs
- Use Firebase Admin SDK for token verification
- Generate signed URLs with short expiration times
- Implement rate limiting for production

### Testing

- Run GPT service tests: `pytest tests/test_gpt_service.py -v`
- Test GPT-5 connection: `python tests/test_gpt5_greeting.py`
- Use admin page for end-to-end testing

## Common Tasks

### Adding a New API Endpoint

1. Create route function in appropriate file (`app/routes/`)
2. Add `@require_firebase_auth` decorator if authentication needed
3. Validate request data
4. Call service layer functions
5. Return JSON response with appropriate status code

### Modifying GPT Behavior

Edit prompts in `app/services/gpt_service.py`:

- `generate_exam_from_text()`: Modify `system_prompt` or `user_prompt`
- `grade_answer()`: Adjust grading criteria in system prompt

### Changing Storage Location

Firebase Storage paths are in `FirebaseStorageService.upload_file()`:

- Current: `pdfs/{user_id}/{uuid}.pdf`
- Modify to organize by date, course, etc.

### Adding New Dependencies

1. Install: `pip install package-name`
2. Freeze: `pip freeze | grep package-name >> requirements.txt`
3. Document in this file if it's a core dependency

## Deployment Considerations

### Environment

- Set `FLASK_ENV=production`
- Use a strong `SECRET_KEY`
- Enable HTTPS only
- Set up proper CORS origins in `config.py`

### Firebase

- Use Firebase project with billing enabled for production
- Configure Storage security rules
- Set up Firestore indexes for queries
- Monitor usage in Firebase Console

### OpenAI

- Monitor API usage and costs
- Implement rate limiting
- Consider caching common exam generations
- Set up usage alerts

### Scaling

- Use WSGI server (Gunicorn, uWSGI)
- Deploy behind reverse proxy (Nginx)
- Consider Firebase Functions for serverless scaling
- Implement job queue for long-running tasks (exam generation)

## Troubleshooting

### Firebase Initialization Failed

- Verify `serviceAccountKey.json` exists and is valid
- Check `FIREBASE_STORAGE_BUCKET` in `.env`
- Ensure Firebase project has Storage enabled

### GPT-5 API Errors

- Verify `OPENAI_API_KEY` is valid
- Check API usage limits
- Review fallback model behavior in logs
- Test with `tests/test_gpt5_greeting.py`

### PDF Upload Fails

- Check file size against `MAX_FILE_SIZE`
- Verify Firebase Storage permissions
- Ensure user is authenticated
- Check Firebase Storage rules

### Authentication Issues

- Verify Firebase ID token is being sent
- Check token hasn't expired (1 hour default)
- Ensure Firebase project matches credentials
- Review Admin SDK initialization logs

## License

MIT License - See LICENSE file for details

---

**For Human Developers**: See README.md for setup instructions  
**For AI Agents**: This document contains the complete technical specification

Last Updated: 2025-10-09
