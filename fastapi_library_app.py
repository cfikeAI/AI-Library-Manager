from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import uvicorn
from PIL import Image
import io
import pandas as pd
from collections import Counter
import sqlite3
from pydantic import BaseModel

import sys
import os
import pytesseract

import pytesseract
print(pytesseract.get_tesseract_version())


#Script imports
import ocr_Photo_Upload
import book_Recommendations
import retrieveMetadata

#FastAPI instance
app = FastAPI(title = "AI-Powered Library Manager")

#Health Check Endpoint
@app.get("/") #decorator for handling GET requests to root URL ('/')
def read_root():
        return {"message": "Welcome to the AI-Powered Library Manager"}

# Combined Endpoint: OCR + Metadata Retrieval
@app.post("/process-book/")
async def process_book(file: UploadFile = File(...), api_key: str = None):
    try:
        # ✅ Read file and convert to a valid PIL image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))  # Convert bytes to a PIL image

        extracted_text = ocr_Photo_Upload.extract_text_from_image(contents)  # ✅ Pass bytes

        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        title = lines[0] if len(lines) > 0 else "Unknown Title"
        author = lines[1] if len(lines) > 1 else "Unknown Author"

        metadata = ocr_Photo_Upload.fetch_book_metadata(title, author, api_key)  # ✅ Fetch metadata

        return {"extracted_text": extracted_text, "metadata": metadata or "Not found", "status": "Success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Endpoint for book recommendations
class UserPreferences(BaseModel):
    user_prefs: str
    method: str = "tfidf"  # Default method if none is provided

@app.post("/recommend-books")
def recommend_books(data: UserPreferences):
    try:
        print(f"Received request: {data.user_prefs}, method: {data.method}")  # Debugging

        # Load books from the database
        books_df = book_Recommendations.load_books_from_db()

        # Determine the recommendation method
        if data.method == "tfidf":
            recommendations = book_Recommendations.generate_recommendations(data.user_prefs, books_df)
        elif data.method == "lucky_draw":
            recommendations = book_Recommendations.lucky_draw(books_df)
        elif data.method == "top_popular":
            recommendations = book_Recommendations.top_popular_books(books_df)
        else:
            raise ValueError("Invalid recommendation method. Choose from: 'tfidf', 'lucky_draw', 'top_popular'.")

        return {"recommendations": recommendations}

    except Exception as e:
        print(f"Error in recommend_books: {str(e)}")  # Print full error
        raise HTTPException(status_code=500, detail=str(e))
    

#Endpoint for rating books
class RatingInput(BaseModel):
    title: str
    rating: float

@app.post("/rate-book")
def rate_book(data: RatingInput):
    try:
        conn = sqlite3.connect("shared/library.db")
        cursor = conn.cursor()

        # Check if the book exists
        cursor.execute("SELECT * FROM books WHERE title = ?", (data.title,))
        book = cursor.fetchone()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found in database.")

        # Update the rating
        cursor.execute("UPDATE books SET rating = ? WHERE title = ?", (data.rating, data.title))
        conn.commit()
        conn.close()

        return {"message": f"Rating for '{data.title}' updated to {data.rating}."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Endpoint for library statistics
@app.get("/stats")
def get_library_statistics():
    try:
        conn = sqlite3.connect("shared/library.db")
        df = pd.read_sql_query("SELECT * FROM books", conn)
        conn.close()

        total_books = len(df)
        most_read_authors = Counter(df["author"].dropna()).most_common(5)
        avg_rating = df["rating"].dropna().mean()

        return {
            "total_books": total_books,
            "most_read_authors": most_read_authors,
            "average_rating": avg_rating
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Endpoint for Library Viewer - Lists all Books in db
@app.get("/books")
def get_books():
    try:
        conn = sqlite3.connect("shared/library.db")
        df = pd.read_sql_query("SELECT title, author, rating FROM books", conn)
        conn.close()
        
        return df.to_dict(orient="records")  # Convert to JSON

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#Run FASTAPI app using Uvicorn when script is executed
if __name__ == "__main__":
     uvicorn.run("fastapi_library_app: app", host = "0.0.0.0", port = 8000, reload = True) #Runs app on localhost (0.0.0.0) on port 8000 w/ auto reload on