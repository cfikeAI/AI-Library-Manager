import pandas as pd
import requests
import time
import os
import sqlite3

# Load your library CSV
library_df = pd.read_csv('Library - Sheet1.csv')

# Create a folder for cover images if it doesn't exist
image_folder = 'cover_images'
os.makedirs(image_folder, exist_ok=True)

# Set up SQLite database
conn = sqlite3.connect('shared/library.db')
cursor = conn.cursor()

# Create books table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        published_date TEXT,
        publisher TEXT,
        page_count INTEGER,
        categories TEXT,
        description TEXT,
        average_rating REAL,
        ratings_count INTEGER,
        isbn TEXT,
        cover_image_path TEXT
    )
''')
conn.commit()

# Google Books API URL
def get_book_data(title, author, api_key=None):
    query = f'{title} {author}'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}'
    if api_key:
        url += f'&key={api_key}'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data:
            return data['items'][0]['volumeInfo']
    return None

# Function to download cover image
def download_cover_image(image_url, title, author):
    if not image_url:
        return None
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Create a safe filename
            safe_title = ''.join(e for e in title if e.isalnum())
            safe_author = ''.join(e for e in author if e.isalnum())
            file_name = f"{safe_title}_{safe_author}.jpg"
            file_path = os.path.join(image_folder, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        print(f"Error downloading image for {title} by {author}: {e}")
    return None

# Replace with your API key if available
API_KEY = None  # e.g., 'YOUR_GOOGLE_BOOKS_API_KEY'

# Fetch metadata and insert into database
for idx, row in library_df.iterrows():
    print(f"Processing book {idx + 1}/{len(library_df)}: {row['Title']} by {row['Author']}")
    book_data = get_book_data(row['Title'], row['Author'], API_KEY)
    
    if book_data:
        published_date = book_data.get('publishedDate')
        publisher = book_data.get('publisher')
        page_count = book_data.get('pageCount')
        categories = ', '.join(book_data.get('categories', []))
        description = book_data.get('description')
        average_rating = book_data.get('averageRating')
        ratings_count = book_data.get('ratingsCount')
        
        # Extract ISBN
        isbn_list = book_data.get('industryIdentifiers', [])
        isbn_values = [isbn['identifier'] for isbn in isbn_list if isbn['type'] in ['ISBN_10', 'ISBN_13']]
        isbn = ', '.join(isbn_values)
        
        # Download and save cover image
        image_links = book_data.get('imageLinks', {})
        image_url = image_links.get('thumbnail')
        cover_image_path = download_cover_image(image_url, row['Title'], row['Author'])
        
        # Insert into database
        cursor.execute('''
            INSERT INTO books (title, author, published_date, publisher, page_count, categories, description, average_rating, ratings_count, isbn, cover_image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['Title'], row['Author'], published_date, publisher, page_count, categories, description, average_rating, ratings_count, isbn, cover_image_path))
        conn.commit()
    else:
        print(f"No metadata found for: {row['Title']} by {row['Author']}")
    
    # To avoid hitting API rate limits
    time.sleep(1)

print("Library metadata enrichment complete! Data saved in 'library.db'.")

# Close database connection
conn.close()
