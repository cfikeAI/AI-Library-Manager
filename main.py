import gradio as gr
import sqlite3
from PIL import Image
import pandas as pd
import io

import ocr_Photo_Upload  # Make sure this matches the filename
import book_Recommendations  # Make sure this matches the filename
import bookRating  # Make sure this matches the filename
import stats # Make sure this matches the filename

# Function to fetch books from the database
def fetch_books():
    conn = sqlite3.connect('library.db')
    query = "SELECT * FROM books"  # Fetch all books
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Function to load cover image from path
def load_cover_image(image_path):
    try:
        with open(image_path, 'rb') as img_file:
            return Image.open(io.BytesIO(img_file.read()))
    except Exception as e:
        return "No Image Available"

# Gradio interface to browse the database
def database_viewer_interface():
    books_df = fetch_books()

    def show_book_details(selected_title):
        book = books_df[books_df['title'] == selected_title].iloc[0]
        cover_image = load_cover_image(book['cover_image_path'])
        book_details = f"""
        **ID:** {book['id']}  
        
        **Title:** {book['title']}  
        
        **Author:** {book['author']}  
        
        **Published Date:** {book['published_date']}  
        
        **Publisher:** {book['publisher']}  
        
        **Page Count:** {book['page_count']}  
        
        **Categories:** {book['categories']}  
        
        **Description:** {book['description']}  
        
        **Rating:** {book['rating']}  
        
        **Ratings Count:** {book['ratings_count']}  
        
        **ISBN:** {book['isbn']}  
        """
        return cover_image, book_details

    with gr.TabItem("View Library"):
        gr.Markdown("## Browse Your Library")
        book_dropdown = gr.Dropdown(choices=books_df['title'].tolist(), label="Select a Book")
        cover_image_output = gr.Image(label="Cover Image", width=200, height=300)
        book_details_output = gr.Markdown(label="Book Details")

        book_dropdown.change(
            show_book_details,
            inputs=book_dropdown,
            outputs=[cover_image_output, book_details_output]
        )

# Main interface combining Photo Upload, Recommendations, and Viewer
def main():
    with gr.Blocks() as demo:
        with gr.Tabs():
            with gr.TabItem("Add Books"):
                ocr_Photo_Upload.photo_upload_interface()

            with gr.TabItem("Book Recommendations"):
                book_Recommendations.recommendation_interface()

            database_viewer_interface()  # Attach and render directly in the Tabs
            bookRating.rate_books_interface()  # New tab for rating books
            stats.reading_statistics_interface() # Tab for reading statistics

    demo.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main()
