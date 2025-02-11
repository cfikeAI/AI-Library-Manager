import pandas as pd
import requests
import time
import os

# Load your library CSV
def load_library_csv(file_path='Library - Sheet1.csv'):
    return pd.read_csv(file_path)

# Create a folder for cover images if it doesn't exist
def ensure_image_folder_exists(folder='cover_images'):
    os.makedirs(folder, exist_ok=True)
    return folder

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
def download_cover_image(image_url, title, author, image_folder='cover_images'):
    if not image_url:
        return None
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
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

# Function to fetch metadata for a specific book
def fetch_metadata(title, author, api_key=None):
    book_data = get_book_data(title, author, api_key)
    if not book_data:
        return None

    metadata = {
        'PublishedDate': book_data.get('publishedDate'),
        'Publisher': book_data.get('publisher'),
        'PageCount': book_data.get('pageCount'),
        'Categories': ', '.join(book_data.get('categories', [])),
        'Description': book_data.get('description'),
        'AverageRating': book_data.get('averageRating'),
        'RatingsCount': book_data.get('ratingsCount'),
    }

    isbn_list = book_data.get('industryIdentifiers', [])
    isbn_values = [isbn['identifier'] for isbn in isbn_list if isbn['type'] in ['ISBN_10', 'ISBN_13']]
    metadata['ISBN'] = ', '.join(isbn_values)

    image_links = book_data.get('imageLinks', {})
    image_url = image_links.get('thumbnail')
    metadata['CoverImagePath'] = download_cover_image(image_url, title, author)

    return metadata

# Only run the following code if this script is executed directly
if __name__ == "__main__":
    library_df = load_library_csv()
    image_folder = ensure_image_folder_exists()
    metadata_columns = ['PublishedDate', 'Publisher', 'PageCount', 'Categories', 'Description', 'AverageRating', 'RatingsCount', 'ISBN', 'CoverImagePath']

    for col in metadata_columns:
        library_df[col] = None

    API_KEY = None  # Add your API key if available

    for idx, row in library_df.iterrows():
        print(f"Processing book {idx + 1}/{len(library_df)}: {row['Title']} by {row['Author']}")
        book_metadata = fetch_metadata(row['Title'], row['Author'], API_KEY)
        
        if book_metadata:
            for key in metadata_columns:
                library_df.at[idx, key] = book_metadata.get(key)
        else:
            print(f"No metadata found for: {row['Title']} by {row['Author']}")
        
        library_df.to_csv('Library_Enriched.csv', index=False)
        time.sleep(1)

    print("Library metadata enrichment complete! Saved as 'Library_Enriched.csv'.")
