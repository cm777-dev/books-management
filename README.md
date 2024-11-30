# Library Management System

A Flask-based library management system with QR code functionality for book lending.

## Features

- Book management (add, view)
- QR code generation for each book
- Book lending system
- User authentication
- Automatic book information retrieval from multiple sources
- Rich book details and reviews
- Author information

## External APIs Required

### 1. Amazon Product Advertising API
- **Required for:** Book prices, reviews, and Amazon-specific information
- **Setup:**
  1. Create an Amazon Associates account at https://affiliate-program.amazon.com/
  2. Sign up for Product Advertising API at https://webservices.amazon.com/paapi5/documentation/
  3. Get your credentials (Access Key, Secret Key, Associate Tag)
- **Note:** This is a paid service with request quotas

### 2. Google Books API
- **Required for:** Book metadata, descriptions, and categories
- **Setup:**
  1. Go to https://console.cloud.google.com/
  2. Create a new project
  3. Enable the Google Books API
  4. Create API credentials
- **Note:** Free tier available with quotas

### 3. OpenLibrary API
- **Required for:** Book covers, author information, and additional metadata
- **Setup:** No registration required
- **Documentation:** https://openlibrary.org/developers/api
- **Note:** Rate limits apply

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cm777-dev/books-management.git
cd books-management
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API credentials:
```env
SECRET_KEY=your-secret-key-here
AMAZON_ACCESS_KEY=your-access-key
AMAZON_SECRET_KEY=your-secret-key
AMAZON_ASSOCIATE_TAG=your-associate-tag
AMAZON_COUNTRY=US
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Register/Login to access the system
2. Add books by entering their ISBN
3. System automatically retrieves:
   - Book details from Google Books
   - Pricing from Amazon
   - Cover images
   - Author information
   - Reviews and ratings
4. Use QR codes to quickly check out books
5. Track book status (available/borrowed)

## Project Structure

```
books-management/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
├── services/
│   └── book_service.py # Book information retrieval service
├── static/
│   ├── style.css      # Custom CSS
│   ├── images/        # Static images
│   └── qr_codes/      # Generated QR codes
└── templates/
    ├── base.html      # Base template
    ├── index.html     # Home page
    ├── add_book.html  # Add book form
    └── book_detail.html # Book details page
```

## API Rate Limits and Quotas

1. Amazon Product Advertising API:
   - Paid service with tiered pricing
   - Request quotas based on your plan

2. Google Books API:
   - 1,000 requests per day for free tier
   - Can be increased with paid API key

3. OpenLibrary API:
   - 100 requests per minute
   - No daily limit

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
