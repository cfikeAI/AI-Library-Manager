AI-Library-Manager

A Scalable, ML-Integrated Personal Library System with Azure DevOps Deployment
Overview

AI-Library-Manager is a modular, cloud-ready application designed for managing personal book collections using machine learning and DevOps best practices.

Key capabilities include:

    Extracting book titles from cover images using OCR (Tesseract)

    Fetching book metadata using the Google Books API

    Recommending similar books using TF-IDF-based search

    Tracking and rating books locally

    Providing analytics on reading behavior and trends

This project integrates FastAPI, Gradio, Docker, Kubernetes, and Azure DevOps pipelines, showcasing real-world deployment workflows even for lightweight AI use cases.
Technology Stack
Component	Technology
API Backend	FastAPI
User Interface	Gradio
OCR Engine	Tesseract
Recommendation	TF-IDF with cosine similarity
Database	SQLite
Containerization	Docker
Orchestration	Kubernetes (Azure AKS)
CI/CD	GitHub Actions
Infrastructure	Azure CLI-based provisioning
Features

    Upload book cover images to automatically extract titles via OCR

    Metadata lookup using Google Books API

    Intelligent recommendations based on similarity to user preferences

    Book rating and collection tracking

    Analytics including top authors, total books, and reading stats

Local Installation
1. Prerequisites

    Python 3.10+

    Tesseract OCR:

        Windows: Tesseract Installation (UB Mannheim)

        Ensure tesseract is added to system PATH

        Verify installation:

        tesseract --version

2. Clone Repository and Install Dependencies

git clone https://github.com/cfikeAI/AI-Library-Manager.git
cd AI-Library-Manager
pip install -r requirements.txt

Azure Deployment (CI/CD + AKS)

All infrastructure was provisioned using Azure CLI commands, avoiding GUI configuration.
API Reference (FastAPI)
Endpoint	Method	Description
/process-book/	POST	Upload image, extract title, fetch metadata
/rate-book/	POST	Rate a book in the local database
/books/	GET	Retrieve full book list
/stats/	GET	Return collection analytics
/recommend-books/	POST	Return recommendations via TF-IDF
Example Request:

{
  "user_prefs": "Dune",
  "method": "tfidf"
}
