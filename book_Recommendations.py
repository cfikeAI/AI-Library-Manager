import sqlite3
import pandas as pd
import requests
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import gradio as gr


#(Simplified NLP with TF-IDF)
    
# Load books from the database
def load_books_from_db(db_path='library.db'):
    conn = sqlite3.connect(db_path)
    query = "SELECT id, title, author, description, rating, ratings_count FROM books WHERE description IS NOT NULL"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Fetch new books from Google Books API with descriptions
def fetch_new_books(query, existing_titles, api_key=None, top_n=3, bestseller_bias=False):
    if bestseller_bias:
        query += " bestseller OR award-winning OR highly-rated"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10"
    if api_key:
        url += f"&key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        new_books = []
        for item in data.get('items', []):
            title = item['volumeInfo'].get('title', '')
            author = ', '.join(item['volumeInfo'].get('authors', []))
            description = item['volumeInfo'].get('description', 'No description available.')
            if title not in existing_titles:
                book_info = f"{title} - {author}\n\n{description}\n\n"
                new_books.append(book_info)
            if len(new_books) == top_n:
                break
        return '\n'.join(new_books) if new_books else "No new books found."
    else:
        return f"Failed to fetch data from Google Books API. Status Code: {response.status_code}"

# Generate book recommendations based on description similarity
def generate_recommendations(book_title, df, api_key=None, top_n=3):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    book_idx = df.index[df['title'] == book_title].tolist()
    if not book_idx:
        return "Book not found in the database. Please add more books to get recommendations."

    book_idx = book_idx[0]
    query = df.iloc[book_idx]['description']
    existing_titles = df['title'].tolist()
    return fetch_new_books(query, existing_titles, api_key, top_n)

# Randomized recommendations with diverse keywords
def lucky_draw(df, api_key=None, top_n=3):
    sample_size = max(1, int(0.1 * len(df)))
    random_descriptions = df['description'].sample(n=sample_size).tolist()

    keywords = []
    for desc in random_descriptions:
        words = desc.split()
        keywords.extend(random.sample(words, min(5, len(words))))

    random_query = " ".join(random.sample(keywords, min(10, len(keywords))))
    existing_titles = df['title'].tolist()
    return fetch_new_books(random_query, existing_titles, api_key, top_n)

# Recommendations based on highly-rated/bestselling books
def top_popular_books(df, api_key=None, top_n=3):
    if 'ratings_count' in df.columns and 'rating' in df.columns:
        sample_size = max(1, int(0.1 * len(df)))
        popular_books = df.sort_values(by=['ratings_count', 'rating'], ascending=False)
        random_descriptions = popular_books['description'].sample(n=sample_size).tolist()

        keywords = []
        for desc in random_descriptions:
            words = desc.split()
            keywords.extend(random.sample(words, min(5, len(words))))

        popular_query = " ".join(random.sample(keywords, min(10, len(keywords))))
        existing_titles = df['title'].tolist()
        recommendations = fetch_new_books(popular_query, existing_titles, api_key, top_n, bestseller_bias=True)
        return f"Similar books trending on the NYT bestseller list:\n\n{recommendations}"
    else:
        return "Ratings data not available in the database."

# Gradio interface for book recommendations
def recommend_books(book_title):
    books_df = load_books_from_db()
    return generate_recommendations(book_title, books_df)

def recommend_lucky_draw():
    books_df = load_books_from_db()
    return lucky_draw(books_df)

def recommend_top_popular():
    books_df = load_books_from_db()
    return top_popular_books(books_df)

 #Launch Gradio Interface
def recommendation_interface():
    with gr.Blocks() as demo:
        with gr.TabItem("Book Recommendations"):
            with gr.Row():
                with gr.Column():
                    book_title_input = gr.Textbox(label="Enter Book Title for Recommendations")
                    recommend_button = gr.Button("Get Recommendations")
                    recommendations_output = gr.Textbox(label="Recommended Books")
                with gr.Column():
                    lucky_draw_button = gr.Button("Lucky Draw")
                    lucky_draw_output = gr.Textbox(label="Lucky Draw Recommendations")
                with gr.Column():
                    top_popular_button = gr.Button("Top Popular Books")
                    top_popular_output = gr.Textbox(label="Top Popular Books Recommendations")

            recommend_button.click(recommend_books, inputs=[book_title_input], outputs=[recommendations_output])
            lucky_draw_button.click(recommend_lucky_draw, outputs=[lucky_draw_output])
            top_popular_button.click(recommend_top_popular, outputs=[top_popular_output])

    #demo.launch()

if __name__ == "__main__":
    recommendation_interface
