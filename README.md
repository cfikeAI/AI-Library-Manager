# AI-Library-Manager
ML-Powered Personal Library Management System

# Overview
-Scans book covers via image files utilizing OCR (Tesseract)
-Automatically fetch metadata via Google Books API
-Get AI-powered book recommendations using TF-IDF vectorization
-Rate and manage personal book collections
-Analyze reading habits with ML-powered statistics

This project integrates FastAPI, Machine Learning, and MLOps tools for a scalable, real-world AI
application.

## Tach Stack
- FastAPI: REST API for book management & AI recommendations
- Gradio: Web UI for interactive book management
- Tesseract OCR: Image-to-text extraction for book covers
- SQLite: Local database storage

## Installation Requirements
1. Install Python 3.10+

2. Clone Repository 
    git clone "https://github.com/cfikeIT/AI-Library-Manager" 
    cd AI-Library-Manager

3. Install dependencies:
    pip install -r requirements.txt

4. This project requires Tesseract-OCR for image processing.
    1. Download and install Tesseract from:
       [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
    2. Add `C:\Program Files\Tesseract-OCR` to your system PATH.
    3. Verify installation with: tesseract --version
5. Run FastAPI Server:
    uvicorn fastapi_library_app:app --reload

6. Access at http://127.0.0.1:8000/docs

### Alternative: Use Docker (No Installation Needed)
Instead of installing Tesseract manually, you can run this project inside a **pre-configured Docker container**:

 1. Build the Docker image:
   docker build -t ai-library-manager .
 2. Run the container:
   docker run -p 8000:8000 ai-library-manager
 3. Access API at: http://127.0.0.1:8000/doc


 ### API Endpoints
 Book Management:
 - POST /process-book/ - Uploads a book cover and fetches metadata
 - POST /rate-book/ - Updates book rating
 - GET /books/ - Fetches all books from the database
 - GET /stats/ - Returns reading statistics (total books, top authors)

 AI-Powered Recommendations:
 - POST /recommend-books/ - Get book recommendations based on AI models
 
 Example Recommendation Request:

{
  "user_prefs": "Dune",
  "method": "tfidf"
}