# test.me Backend API 📚

> AI-powered exam generation and grading system backend that analyzes lecture PDFs using GPT-5

## Overview

**test.me** is a Flask-based REST API that powers an AI-driven learning platform. Users upload university lecture PDFs, and GPT-5 generates customized exam questions. The system then automatically grades student submissions and provides feedback.

### Core Concept

1. User uploads a lecture PDF via Android app
2. GPT-5 analyzes the PDF and generates exam questions
3. User submits answers
4. GPT-5 grades the answers and provides feedback

## Tech Stack

- **Framework**: Flask 3.0.3
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

Create a `.env` file in the root directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
OPENAI_API_KEY=your-openai-api-key-here
```

5. **Run the development server**

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
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
├── LICENSE            # MIT License
├── README.md          # Project documentation
│
├── app/               # Main application package
│   ├── __init__.py
│   ├── models/        # Database models
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic (GPT service, PDF processor, etc.)
│   └── utils/         # Utility functions
│
├── uploads/           # Uploaded PDF files
├── public/            # Static files
├── migrations/        # Database migrations
└── venv/             # Virtual environment (not in git)
```

## Development Status

This project is in early development stage. Core features are being designed and implemented.

## License

This project is licensed under the MIT License.

---

Built with ❤️ for students
