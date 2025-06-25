import gradio as gr
import sqlite3
from PIL import Image
import pandas as pd
import io


# Gradio interface to rate books in the database

# Function to fetch books from the database
def fetch_books():
    conn = sqlite3.connect('shared/library.db')
    query = "SELECT * FROM books"  # Fetch all books
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def rate_books_interface():
    books_df = fetch_books()

    def update_rating(selected_title, rating):
        conn = sqlite3.connect('shared/library.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE books SET rating = ? WHERE title = ?", (rating, selected_title))
        conn.commit()
        conn.close()
        return f"Rating updated! {selected_title} now has a rating of {rating}."

    with gr.TabItem("Rate Books"):
        gr.Markdown("## Rate a Book in Your Library")
        book_dropdown = gr.Dropdown(choices=books_df['title'].tolist(), label="Select a Book")
        rating_slider = gr.Slider(minimum=1, maximum=5, step=1, label="Rate this Book (1-5)")
        status_output = gr.Textbox(label="Status", interactive=False)

        rating_slider.change(
            update_rating,
            inputs=[book_dropdown, rating_slider],
            outputs=status_output
        )