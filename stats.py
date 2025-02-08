import gradio as gr
import sqlite3
from PIL import Image
import pandas as pd
import io
import matplotlib.pyplot as plt
from collections import Counter

# Function to fetch books from the database
def fetch_books():
    conn = sqlite3.connect('library.db')
    query = "SELECT * FROM books"  # Fetch all books
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Gradio interface for reading statistics
def reading_statistics_interface():
    books_df = fetch_books()

    def plot_total_books():
        total_books = len(books_df)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(['Total Books'], [total_books], color='#4A90E2', edgecolor='black')
        ax.set_ylabel('Number of Books', fontsize=12)
        ax.set_title('Total Books in Library', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def plot_most_read_authors():
        authors = books_df['author'].dropna().tolist()
        author_counts = Counter(authors).most_common(5)
        authors, counts = zip(*author_counts)
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(authors, counts, color='#FF6F61', edgecolor='black')
        ax.set_xlabel('Number of Books', fontsize=12)
        ax.set_title('Top 5 Most Read Authors', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Show the highest bar at the top
        
        for bar in bars:
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(bar.get_width()), va='center', fontsize=10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def plot_average_ratings():
        ratings = books_df['rating'].dropna().astype(float)
        if ratings.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No Ratings Available', horizontalalignment='center', verticalalignment='center', fontsize=12)
            ax.axis('off')
            return fig

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(ratings, bins=5, color='#50C878', edgecolor='black', alpha=0.8)
        ax.set_xlabel('Ratings', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Book Ratings', fontsize=14, fontweight='bold')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    with gr.TabItem("Reading Statistics"):
        gr.Markdown("## Your Library Stats")
        total_books_plot = gr.Plot(label="Total Books", value=plot_total_books)
        most_read_authors_plot = gr.Plot(label="Most Read Authors", value=plot_most_read_authors)
        average_ratings_plot = gr.Plot(label="Average Ratings", value=plot_average_ratings)