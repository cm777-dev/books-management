import requests
from bs4 import BeautifulSoup
import isbnlib
from datetime import datetime
import os
from dotenv import load_dotenv
from amazon.paapi import AmazonAPI

load_dotenv()

class BookService:
    def __init__(self):
        self.google_books_api = "https://www.googleapis.com/books/v1/volumes"
        self.openlibrary_api = "https://openlibrary.org/api/books"
        
        # Initialize Amazon API client
        self.amazon = AmazonAPI(
            os.getenv('AMAZON_ACCESS_KEY'),
            os.getenv('AMAZON_SECRET_KEY'),
            os.getenv('AMAZON_ASSOCIATE_TAG'),
            os.getenv('AMAZON_COUNTRY', 'US')
        )
    
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
            
        # Get Amazon data
        amazon_data = self._get_amazon_data(isbn)
        if amazon_data:
            book_data.update(amazon_data)
            
        # Get book cover (prioritize Amazon cover if available)
        if amazon_data and amazon_data.get('cover_url'):
            book_data['cover_url'] = amazon_data['cover_url']
        else:
            book_data['cover_url'] = self.get_book_cover(isbn)
        
        return book_data
    
    def _get_amazon_data(self, isbn):
        """Retrieve book data from Amazon API"""
        try:
            items = self.amazon.search_items(keywords=isbn)
            if items and len(items) > 0:
                item = items[0]
                return {
                    'title': item.item_info.title.display_value,
                    'author': item.item_info.by_line_info.contributors[0].name,
                    'amazon_url': item.detail_page_url,
                    'cover_url': item.images.primary.large.url,
                    'price': item.offers.listings[0].price.display_amount if item.offers and item.offers.listings else None,
                    'amazon_rating': item.item_info.rating.rating if hasattr(item.item_info, 'rating') else None,
                    'amazon_review_count': item.item_info.rating.count if hasattr(item.item_info, 'rating') else None,
                    'prime_eligible': item.offers.listings[0].delivery_info.is_prime_eligible if item.offers and item.offers.listings else False,
                    'manufacturer': item.item_info.by_line_info.manufacturer.display_value if hasattr(item.item_info.by_line_info, 'manufacturer') else None,
                }
        except Exception as e:
            print(f"Error fetching Amazon data: {e}")
        return {}

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
                        
                        # Try to get Amazon author page
                        amazon_author_url = None
                        try:
                            author_search = self.amazon.search_items(keywords=f"author {author_name}")
                            if author_search and len(author_search) > 0:
                                amazon_author_url = f"https://www.amazon.com/stores/{author_name.replace(' ', '-')}/author/about"
                        except:
                            pass
                            
                        return {
                            'name': author_data.get('name'),
                            'birth_date': author_data.get('birth_date'),
                            'bio': author_data.get('bio', {}).get('value', ''),
                            'wikipedia': author_data.get('wikipedia'),
                            'amazon_page': amazon_author_url,
                            'photos': [f"https://covers.openlibrary.org/a/id/{photo_id}-L.jpg" 
                                     for photo_id in author_data.get('photos', [])]
                        }
        except Exception as e:
            print(f"Error fetching author info: {e}")
        return {}

    def get_book_reviews(self, isbn):
        """Get book reviews from multiple sources including Amazon"""
        reviews = []
        
        try:
            # Get Amazon reviews
            items = self.amazon.search_items(keywords=isbn)
            if items and len(items) > 0:
                item = items[0]
                if hasattr(item.item_info, 'rating'):
                    reviews.append({
                        'source': 'Amazon',
                        'rating': item.item_info.rating.rating,
                        'review_count': item.item_info.rating.count,
                        'url': item.detail_page_url
                    })
            
            # Get Goodreads metadata
            metadata = isbnlib.meta(isbn)
            if metadata:
                reviews.append({
                    'source': 'Goodreads',
                    'rating': metadata.get('Year', 0),
                    'review_count': len(metadata.get('Authors', [])) * 100,
                    'url': f"https://www.goodreads.com/book/isbn/{isbn}"
                })
            
        except Exception as e:
            print(f"Error fetching book reviews: {e}")
        
        return reviews

    def validate_isbn(self, isbn):
        """Validate ISBN number"""
        return isbnlib.is_isbn13(isbn) or isbnlib.is_isbn10(isbn)
