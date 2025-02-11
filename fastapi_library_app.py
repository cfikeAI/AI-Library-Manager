from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import uvicorn

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
        # Step 1: Extract Text from Book Cover
        extracted_text = ocr_Photo_Upload.extract_text_from_image(file.file)

        # Step 2: Parse Title and Author from Extracted Text
        lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
        title = lines[0] if len(lines) > 0 else "Unknown Title"
        author = lines[1] if len(lines) > 1 else "Unknown Author"

        # Step 3: Fetch Metadata Using Google Books API
        metadata = ocr_Photo_Upload.process_image(title, author, api_key)

        # Step 4: Return Combined Response
        if metadata:
            return {
                "extracted_text": extracted_text,
                "metadata": metadata,
                "status": "Metadata fetched successfully."
            }
        else:
            return {
                "extracted_text": extracted_text,
                "metadata": "Metadata not found. Please verify the extracted text.",
                "status": "Could not fetch metadata."
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#Endpoint for book recommendations
@app.post("/recommend-books")
def recommend_books(user_prefs: str): #accepts user preferences as string for recommendation generation
     try:
          recommendations = book_Recommendations.generate_recommendations(user_prefs) #calls function from book_recommendations
          return {"recommendations" : recommendations} #returns recommendations as JSON
     except Exception as e:
          raise HTTPException(status_code= 500, detail = str(e)) #return 500 error message for errors


#Run FASTAPI app using Uvicorn when script is executed
if __name__ == "__main__":
     uvicorn.run("fastapi_library_app: app", host = "0.0.0.0", port = 8000, reload = True) #Runs app on localhost (0.0.0.0) on port 8000 w/ auto reload on