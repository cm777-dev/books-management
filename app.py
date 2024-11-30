from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import qrcode
from datetime import datetime
import os
from services.book_service import BookService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
book_service = BookService()

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(13), unique=True)
    status = db.Column(db.String(20), default='available')
    qr_code = db.Column(db.String(200))
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    published_date = db.Column(db.String(50))
    publisher = db.Column(db.String(100))
    page_count = db.Column(db.Integer)
    average_rating = db.Column(db.Float)
    categories = db.Column(db.String(200))
    preview_link = db.Column(db.String(500))

class Lending(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checkout_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/book/<isbn>')
def book_detail(isbn):
    book = Book.query.filter_by(isbn=isbn).first_or_404()
    author_info = book_service.get_author_info(book.author)
    reviews = book_service.get_book_reviews(isbn)
    return render_template('book_detail.html', book=book, author_info=author_info, reviews=reviews)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        
        # Validate ISBN
        if not book_service.validate_isbn(isbn):
            flash('Invalid ISBN number', 'error')
            return redirect(url_for('add_book'))
            
        # Get book details from various sources
        book_details = book_service.get_book_details(isbn)
        
        # Create new book
        book = Book(
            title=book_details.get('title'),
            author=', '.join(book_details.get('authors', [])),
            isbn=isbn,
            description=book_details.get('description'),
            cover_url=book_details.get('cover_url'),
            published_date=book_details.get('published_date'),
            publisher=', '.join(book_details.get('publisher', [])),
            page_count=book_details.get('page_count'),
            average_rating=book_details.get('average_rating'),
            categories=', '.join(book_details.get('categories', [])),
            preview_link=book_details.get('preview_link')
        )
        
        # Generate QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'book:{isbn}')
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_filename = f'qr_code_{isbn}.png'
        qr_path = os.path.join('static', 'qr_codes', qr_filename)
        qr_image.save(qr_path)
        book.qr_code = qr_filename
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('book_detail', isbn=isbn))
    
    return render_template('add_book.html')

@app.route('/api/book/<isbn>')
def api_book_details(isbn):
    """API endpoint to get book details"""
    book_details = book_service.get_book_details(isbn)
    return jsonify(book_details)

@app.route('/lend_book/<int:book_id>', methods=['POST'])
@login_required
def lend_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.status == 'available':
        lending = Lending(book_id=book_id, user_id=current_user.id)
        book.status = 'borrowed'
        db.session.add(lending)
        db.session.commit()
        flash('Book borrowed successfully!', 'success')
    else:
        flash('Book is not available!', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('static/qr_codes'):
            os.makedirs('static/qr_codes')
        db.create_all()
    app.run(debug=True)
