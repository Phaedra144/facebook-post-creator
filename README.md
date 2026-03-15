# Facebook Post Creator

A Python FastAPI application that automatically generates and posts content to Facebook using AI-powered text generation (via Groq) and programmatic cover image generation.

## Project Overview

The application includes:
- **Python Backend**: FastAPI server for managing posts and Facebook integration
- **Cover Generator**: Node.js sub-package using React and Satori for generating cover images
- **Database**: SQLite for storing posts, categories, and sources
- **AI Integration**: Groq API for content generation

## Prerequisites

- Python 3.8+
- Node.js 16+ (for cover-gen)
- Groq API key
- Facebook page credentials (Page ID and Access Token)

## Setup

### 1. Environment Configuration

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:
```
GROQ_API_KEY=your_groq_api_key_here
FB_PAGE_ID=your_facebook_page_id_here
FB_PAGE_ACCESS_TOKEN=your_facebook_page_access_token_here
DATABASE_URL=sqlite:///./facebook-creator.db
```

### 2. Install Python Dependencies

Create and activate a virtual environment:

```bash
python -m venv facebook-venv
source facebook-venv/bin/activate  # On Windows: facebook-venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install Node.js Dependencies (for cover-gen)

```bash
cd cover-gen
npm install
cd ..
```

## Starting the Application

### Start the FastAPI Server

With the virtual environment activated:

```bash
python -m app.main
```

The API will start on `http://localhost:8000`

**API Documentation** (interactive):
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Cover Generator

To build and test the cover generator:

```bash
cd cover-gen
npm run render
```

## Shutting Down

### Stop the FastAPI Server

Simple Ctrl + C does not work

```bash
kill -9 $(lsof -ti :8000)
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Key Endpoints

- `GET /` - Health check
- `POST /posts` - Create a new Facebook post
- Additional endpoints available in `/docs`

## Development Notes

- The database is automatically created on first run
- Posts are stored in `facebook-creator.db`
- Hot reload is enabled during development
- Changes to Python files automatically restart the server
