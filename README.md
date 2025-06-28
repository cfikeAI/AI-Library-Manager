AI-Library-Manager

A scalable, containerized book library app that extracts metadata from cover images, recommends similar titles, and tracks user reading behavior — deployed end-to-end with Azure AKS, GitHub Actions, and Docker.
What It Does

    -Extracts book titles from cover images using OCR (Tesseract)

    -Queries Google Books API to pull metadata automatically

    -Recommends similar books using TF-IDF vectorization

    -Lets users rate and track their book collection

    -Generates basic reading analytics (top authors, total read, etc.)

All services are containerized, orchestrated via Kubernetes, and deployed to Azure using an automated CI/CD pipeline.
Tech Stack
Layer	Tech
Backend	FastAPI for RESTful metadata and recommendation API
Frontend	Gradio interface for uploading covers, rating books, and analytics
OCR	Tesseract (via pytesseract) for image-to-text
ML	TF-IDF-based recommendation engine (scikit-learn)
Database	SQLite (mounted volume for shared access across services)
Infra	Docker + Kubernetes (Azure AKS) + GitHub Actions + ACR
CI/CD	Full GitHub Actions pipeline for auto-deploying on main push

              +-------------------+
              |    User Uploads   |
              |  Book Cover Image |
              +-------------------+
                       |
                       v
          +-------------------------+
          |   Gradio Frontend (UI)  |
          +-------------------------+
                       |
                       v
      +----------------------------------+
      |  FastAPI Backend (OCR + ML API)  |
      +----------------------------------+
             |                  |
             |                  v
             v         +------------------+
     +-------------+   | Google Books API |
     | SQLite DB   |   +------------------+
     +-------------+
Local Dev Setup
1. Install Dependencies

git clone https://github.com/cfikeAI/AI-Library-Manager.git
cd AI-Library-Manager
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

2. Install Tesseract

    Ubuntu: sudo apt install tesseract-ocr

    Windows: Tesseract Install (UB Mannheim)

Make sure tesseract is in your system path.


Azure CI/CD Pipeline

    Push to main triggers a full GitHub Actions pipeline

    Docker images are built and pushed to Azure Container Registry (ACR)

    Kubernetes manifests (/k8s/) are automatically applied via kubectl

    App is deployed to Azure AKS with zero manual interaction

