import os
import sqlite3
import requests
from PIL import Image
import pytesseract
import io
import gradio as gr
import pandas

import os
import pytesseract



# Create directory for uploaded images
UPLOAD_FOLDER = 'uploaded_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fetch book metadata using Google Books API
def fetch_book_metadata(title, author, api_key=None):
    query = f"{title} {author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    if api_key:
        url += f"&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            book_info = data['items'][0]['volumeInfo']
            return {
                'title': book_info.get('title', title),
                'author': ', '.join(book_info.get('authors', [author])),
                'published_date': book_info.get('publishedDate', ''),
                'publisher': book_info.get('publisher', ''),
                'page_count': book_info.get('pageCount', 0),
                'categories': ', '.join(book_info.get('categories', [])),
                'description': book_info.get('description', ''),
                'rating': book_info.get('Rating', 0.0),
                'ratings_count': book_info.get('ratingsCount', 0),
                'isbn': ', '.join([
                    identifier.get('identifier', '')
                    for identifier in book_info.get('industryIdentifiers', [])
                ]),
                'cover_image_url': book_info.get('imageLinks', {}).get('thumbnail', '')
            }
    return None

# Insert new book into the database
def insert_new_book(metadata, new_img_path):
    conn = sqlite3.connect('shared/library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books WHERE title = ? AND author = ?", (metadata['title'], metadata['author']))
    if cursor.fetchone():
        return f"Book '{metadata['title']}' by {metadata['author']} already exists in the database."

    cursor.execute('''
        INSERT INTO books (
            title, author, published_date, publisher, page_count, categories, 
            description, rating, ratings_count, isbn, cover_image_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        metadata['title'], metadata['author'], metadata['published_date'], 
        metadata['publisher'], metadata['page_count'], metadata['categories'], 
        metadata['description'], metadata['rating'], metadata['ratings_count'], 
        metadata['isbn'], new_img_path
    ))

    conn.commit()
    conn.close()
    return f"New book '{metadata['title']}' by {metadata['author']} added to the database."

# Extract text from book cover using OCR
def extract_text_from_image(image):
    try:
        # ✅ Ensure the image is a PIL Image
        if isinstance(image, bytes):
            image = Image.open(io.BytesIO(image))  # Convert bytes to PIL Image
        
        elif not isinstance(image, Image.Image):  # If it's not already a PIL image
            raise ValueError("Unsupported image object. Expected a valid image.")

        # ✅ Perform OCR with pytesseract
        text = pytesseract.image_to_string(image)
        
        return text
    except Exception as e:
        raise ValueError(f"Unsupported image object: {e}")

# Gradio interface function
def process_image(image, api_key=None):
    extracted_text = extract_text_from_image(image)

    # Save uploaded image
    image_filename = os.path.join(UPLOAD_FOLDER, 'uploaded_book_cover.jpg')
    image.save(image_filename)

    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
    title = lines[0] if len(lines) > 0 else "Unknown Title"
    author = lines[1] if len(lines) > 1 else "Unknown Author"

    metadata = fetch_book_metadata(title, author, api_key)
    if metadata:
        metadata_display = f"""
        **Title:** {metadata['title']}\n
        **Author:** {metadata['author']}\n
        **Published Date:** {metadata['published_date']}\n
        **Publisher:** {metadata['publisher']}\n
        **Page Count:** {metadata['page_count']}\n
        **Categories:** {metadata['categories']}\n
        **Description:** {metadata['description']}\n
        **Average Rating:** {metadata['rating']}\n
        **Ratings Count:** {metadata['ratings_count']}\n
        **ISBN:** {metadata['isbn']}\n
        **Cover Image URL:** {metadata['cover_image_url']}\n
        """
        return extracted_text, metadata_display, "Metadata fetched. Please confirm to add to the database."
    else:
        return extracted_text, "Metadata not found. Please verify the extracted text.", "Could not fetch metadata. Book not added."

# Confirm button functionality
def confirm_addition(image, api_key=None):
    extracted_text = extract_text_from_image(image)
    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
    title = lines[0] if len(lines) > 0 else "Unknown Title"
    author = lines[1] if len(lines) > 1 else "Unknown Author"

    metadata = fetch_book_metadata(title, author, api_key)
    if metadata:
        result_message = insert_new_book(metadata, os.path.join(UPLOAD_FOLDER, 'uploaded_book_cover.jpg'))
        return extracted_text, f"Book '{metadata['title']}' by {metadata['author']} added to the database.", result_message
    else:
        return extracted_text, "Metadata not found. Cannot add to database.", "Book not added."

# Clear button functionality
def clear_all():
    return None, "", "", ""

# Launch Gradio Interface
def photo_upload_interface():
    with gr.Blocks() as demo:
        with gr.Row():
            image_input = gr.Image(type="pil", label="Upload Book Cover")
        with gr.Row():
            extracted_text_output = gr.Textbox(label="Extracted Text from Cover")
            metadata_output = gr.Textbox(label="Fetched Book Metadata")
            status_output = gr.Textbox(label="Database Status")
        with gr.Row():
            confirm_button = gr.Button("Confirm Book Addition")
            clear_button = gr.Button("Clear")

        image_input.change(process_image, inputs=image_input, outputs=[extracted_text_output, metadata_output, status_output])
        confirm_button.click(confirm_addition, inputs=[image_input], outputs=[extracted_text_output, metadata_output, status_output])
        clear_button.click(clear_all, inputs=[], outputs=[image_input, extracted_text_output, metadata_output, status_output])

    #demo.launch()

if __name__ == "__main__":
    photo_upload_interface()
