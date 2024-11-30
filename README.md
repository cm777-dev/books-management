# Library Management System

A Flask-based library management system with QR code functionality for book lending.

## Features

- Book management (add, view)
- QR code generation for each book
- Book lending system
- User authentication
- Responsive UI with Bootstrap

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

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Register/Login to access the system
2. Add books through the "Add Book" interface
3. Each book will automatically generate a QR code
4. Use the QR code to quickly check out books
5. Track book status (available/borrowed)

## Project Structure

```
books-management/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css      # Custom CSS
│   └── qr_codes/      # Generated QR codes
└── templates/
    ├── base.html      # Base template
    ├── index.html     # Home page
    └── add_book.html  # Add book form
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
