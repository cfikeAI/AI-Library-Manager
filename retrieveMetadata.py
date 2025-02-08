import pandas as pd
import requests
import time
import os

# Load your library CSV
library_df = pd.read_csv('Library - Sheet1.csv')

# Create a folder for cover images if it doesn't exist
image_folder = 'cover_images'
os.makedirs(image_folder, exist_ok=True)

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

# Columns to add
metadata_columns = ['PublishedDate', 'Publisher', 'PageCount', 'Categories', 'Description', 'AverageRating', 'RatingsCount', 'ISBN', 'CoverImagePath']

# Initialize new columns
for col in metadata_columns:
    library_df[col] = None

# Replace with your API key if available
API_KEY = None  # e.g., 'YOUR_GOOGLE_BOOKS_API_KEY'

# Fetch metadata
for idx, row in library_df.iterrows():
    print(f"Processing book {idx + 1}/{len(library_df)}: {row['Title']} by {row['Author']}")
    book_data = get_book_data(row['Title'], row['Author'], API_KEY)
    
    if book_data:
        library_df.at[idx, 'PublishedDate'] = book_data.get('publishedDate')
        library_df.at[idx, 'Publisher'] = book_data.get('publisher')
        library_df.at[idx, 'PageCount'] = book_data.get('pageCount')
        library_df.at[idx, 'Categories'] = ', '.join(book_data.get('categories', []))
        library_df.at[idx, 'Description'] = book_data.get('description')
        library_df.at[idx, 'AverageRating'] = book_data.get('averageRating')
        library_df.at[idx, 'RatingsCount'] = book_data.get('ratingsCount')
        
        # Extract ISBN
        isbn_list = book_data.get('industryIdentifiers', [])
        isbn_values = [isbn['identifier'] for isbn in isbn_list if isbn['type'] in ['ISBN_10', 'ISBN_13']]
        library_df.at[idx, 'ISBN'] = ', '.join(isbn_values)
        
        # Download and save cover image
        image_links = book_data.get('imageLinks', {})
        image_url = image_links.get('thumbnail')
        cover_image_path = download_cover_image(image_url, row['Title'], row['Author'])
        library_df.at[idx, 'CoverImagePath'] = cover_image_path
    else:
        print(f"No metadata found for: {row['Title']} by {row['Author']}")
    
    # Save progress after each book
    library_df.to_csv('Library_Enriched.csv', index=False)
    
    # To avoid hitting API rate limits
    time.sleep(1)

print("Library metadata enrichment complete! Saved as 'Library_Enriched.csv'.")
