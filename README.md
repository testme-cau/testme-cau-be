# test.me Backend API 📚

> AI-powered exam generation and grading system backend that analyzes lecture PDFs using GPT-5

## Overview

**test.me** is a Flask-based REST API that powers an AI-driven learning platform. Users upload university lecture PDFs, and GPT-5 generates customized exam questions. The system then automatically grades student submissions and provides feedback.

### Core Concept

1. User authenticates via Firebase OAuth 2.0 (Android app) or admin login (web interface)
2. User uploads a lecture PDF via Android app
3. PDF is uploaded to OpenAI via Assistants API
4. GPT-5 directly reads and analyzes the PDF (including text, images, tables)
5. GPT-5 generates customized exam questions
6. User submits answers
7. GPT-5 grades the answers by referencing the original PDF and provides feedback

## Tech Stack

- **Framework**: Flask 3.0.3
- **Authentication**: Firebase OAuth 2.0 (with Firebase Admin SDK)
- **Database**: Cloud Firestore (NoSQL document database)
- **Storage**: Firebase Cloud Storage (PDF file storage with signed URLs)
- **AI Integration**: OpenAI GPT-5 API
- **Python**: 3.8+

## Getting Started

### Prerequisites

- Python 3.8+
- pip

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
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Server Configuration
HOST=0.0.0.0
PORT=5000

# File Upload
MAX_FILE_SIZE=16777216

# Firebase Storage
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# Firebase Web SDK (for Google OAuth login on admin page)
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

# OpenAI API
OPENAI_API_KEY=your-openai-api-key-here

# Admin Page (for web testing - legacy, OAuth recommended)
ADMIN_ID=admin
ADMIN_PW=your-secure-password
```

5. **Set up Firebase credentials**

Download your Firebase service account key JSON file from Firebase Console and save it as `serviceAccountKey.json` in the project root (this file is ignored by git).

6. **Run the development server**

```bash
flask run
```

The API will be available at `http://localhost:5000`

## Project Structure

```
be/
├── app.py              # Flask application entry point
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
├── LICENSE            # MIT License
├── README.md          # Project documentation
│
├── app/               # Main application package
│   ├── __init__.py
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic (GPT service with Assistants API, Firebase Storage, etc.)
│   └── utils/         # Utility functions
│
├── public/            # Static files
├── serviceAccountKey.json  # Firebase service account key (not in git)
└── venv/             # Virtual environment (not in git)

Note:
- PDF files are stored in Firebase Cloud Storage
- Files are accessible via signed URLs (1-hour expiration)
- Metadata is stored in Cloud Firestore (NoSQL)
```

## Authentication

### Firebase OAuth 2.0 (Android App)

Users authenticate through Firebase OAuth 2.0 in the Android app. All API endpoints (except `/` and `/health`) require a Firebase ID token in the `Authorization` header.

### Admin Login (Web Interface)

For development and testing purposes, an admin web interface with **Google OAuth 2.0** is available at `/admin-page`.

#### Access

1. Navigate to `http://localhost:5000/admin-page`
2. Click **"Sign in with Google"** button
3. Authenticate with your Google account via Firebase
4. Access the dashboard with full API functionality

#### Firebase Configuration

To enable Google OAuth on the admin page, you need to configure Firebase Web SDK:

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Project Settings** → **General**
4. Scroll to **Your apps** and select/add a Web app
5. Copy the configuration values to your `.env`:
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
6. Enable **Google Sign-In** in **Authentication** → **Sign-in method**

#### Features

The admin page allows you to:

- **Authenticate** with real Firebase Google OAuth 2.0
- **Upload PDFs** and generate exams via web interface
- **Test API** functionality without Android app
- **Debug** backend operations with real Firebase tokens

#### Legacy Admin Login

A legacy username/password login is still available for backward compatibility:
- Set `ADMIN_ID` and `ADMIN_PW` in `.env`
- This creates a mock Firebase user without real tokens
- **Not recommended**: Use Google OAuth instead for realistic testing

**Note**: Admin OAuth login simulates the actual Android app authentication flow.

## Development Status

This project is in early development stage. Core features are being designed and implemented.

## License

This project is licensed under the MIT License.

---

Built with ❤️ for students
