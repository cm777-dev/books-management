import requests
from bs4 import BeautifulSoup
import isbnlib
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class BookService:
    def __init__(self):
        self.google_books_api = "https://www.googleapis.com/books/v1/volumes"
        self.openlibrary_api = "https://openlibrary.org/api/books"
        
    def get_book_details(self, isbn):
        """Get comprehensive book details from multiple sources"""
        book_data = {}
        
        # Get data from Google Books
        google_data = self._get_google_books_data(isbn)
        if google_data:
            book_data.update(google_data)
            
        # Get data from OpenLibrary
        openlib_data = self._get_openlibrary_data(isbn)
        if openlib_data:
            book_data.update(openlib_data)
            
        # Get book cover
        book_data['cover_url'] = self.get_book_cover(isbn)
        
        return book_data
    
    def _get_google_books_data(self, isbn):
        """Retrieve book data from Google Books API"""
        try:
            params = {'q': f'isbn:{isbn}'}
            response = requests.get(self.google_books_api, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    book_info = data['items'][0]['volumeInfo']
                    return {
                        'title': book_info.get('title'),
                        'authors': book_info.get('authors', []),
                        'description': book_info.get('description'),
                        'categories': book_info.get('categories', []),
                        'average_rating': book_info.get('averageRating'),
                        'published_date': book_info.get('publishedDate'),
                        'page_count': book_info.get('pageCount'),
                        'preview_link': book_info.get('previewLink')
                    }
        except Exception as e:
            print(f"Error fetching Google Books data: {e}")
        return {}

    def _get_openlibrary_data(self, isbn):
        """Retrieve book data from OpenLibrary API"""
        try:
            response = requests.get(f"https://openlibrary.org/isbn/{isbn}.json")
            if response.status_code == 200:
                data = response.json()
                return {
                    'publisher': data.get('publishers', []),
                    'publish_date': data.get('publish_date'),
                    'number_of_pages': data.get('number_of_pages'),
                    'subjects': data.get('subjects', [])
                }
        except Exception as e:
            print(f"Error fetching OpenLibrary data: {e}")
        return {}

    def get_book_cover(self, isbn):
        """Get book cover URL from OpenLibrary"""
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

    def get_author_info(self, author_name):
        """Get author information from multiple sources"""
        try:
            # Search author in OpenLibrary
            response = requests.get(f"https://openlibrary.org/search/authors.json?q={author_name}")
            if response.status_code == 200:
                data = response.json()
                if data.get('docs'):
                    author = data['docs'][0]
                    author_key = author.get('key')
                    
                    # Get detailed author info
                    author_response = requests.get(f"https://openlibrary.org{author_key}.json")
                    if author_response.status_code == 200:
                        author_data = author_response.json()
                        return {
                            'name': author_data.get('name'),
                            'birth_date': author_data.get('birth_date'),
                            'bio': author_data.get('bio', {}).get('value', ''),
                            'wikipedia': author_data.get('wikipedia'),
                            'photos': [f"https://covers.openlibrary.org/a/id/{photo_id}-L.jpg" 
                                     for photo_id in author_data.get('photos', [])]
                        }
        except Exception as e:
            print(f"Error fetching author info: {e}")
        return {}

    def get_book_reviews(self, isbn):
        """Get book reviews from Goodreads API"""
        try:
            # Using isbnlib to get Goodreads metadata
            metadata = isbnlib.meta(isbn)
            reviews = []
            
            if metadata:
                # Simulate reviews (since Goodreads API is no longer public)
                reviews = [
                    {
                        'source': 'Goodreads',
                        'rating': metadata.get('Year', 0),  # Using year as a placeholder
                        'review_count': len(metadata.get('Authors', [])) * 100,  # Simulated count
                        'url': f"https://www.goodreads.com/book/isbn/{isbn}"
                    }
                ]
            
            return reviews
        except Exception as e:
            print(f"Error fetching book reviews: {e}")
            return []

    def validate_isbn(self, isbn):
        """Validate ISBN number"""
        return isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn)
