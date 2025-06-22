import gradio as gr
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Fetch all books as a DataFrame
def fetch_books():
    conn = sqlite3.connect('library.db')
    try:
        df = pd.read_sql_query("SELECT * FROM books", conn)
    except Exception:
        df = pd.DataFrame()  # Return empty DataFrame on failure
    finally:
        conn.close()
    return df

# Gradio tab interface for reading statistics
def reading_statistics_interface():
    books_df = fetch_books()

    def plot_total_books():
        fig, ax = plt.subplots(figsize=(6, 4))
        total_books = len(books_df)

        if total_books == 0:
            ax.text(0.5, 0.5, 'No books in library yet', ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        ax.bar(['Total Books'], [total_books], color='#4A90E2', edgecolor='black')
        ax.set_ylabel('Number of Books', fontsize=12)
        ax.set_title('Total Books in Library', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def plot_most_read_authors():
        authors = books_df['author'].dropna().tolist() if 'author' in books_df else []
        author_counts = Counter(authors).most_common(5)

        fig, ax = plt.subplots(figsize=(8, 5))

        if not author_counts:
            ax.text(0.5, 0.5, 'No Author Data Available', ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        labels, counts = zip(*author_counts)
        bars = ax.barh(labels, counts, color='#FF6F61', edgecolor='black')
        ax.set_xlabel('Number of Books', fontsize=12)
        ax.set_title('Top 5 Most Read Authors', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        for bar in bars:
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(bar.get_width()), va='center', fontsize=10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    def plot_average_ratings():
        if 'rating' not in books_df or books_df['rating'].dropna().empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No Ratings Available', ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        ratings = books_df['rating'].dropna().astype(float)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(ratings, bins=5, color='#50C878', edgecolor='black', alpha=0.8)
        ax.set_xlabel('Ratings', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Book Ratings', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        return fig

    # Gradio layout
    with gr.TabItem("Reading Statistics"):
        gr.Markdown("## Your Library Stats")
        gr.Plot(label="Total Books", value=plot_total_books)
        gr.Plot(label="Most Read Authors", value=plot_most_read_authors)
        gr.Plot(label="Average Ratings", value=plot_average_ratings)
