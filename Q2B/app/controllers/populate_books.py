from app.app import create_app, db
from models.books import Book
from models.books import all_books  # <-- import your all_books list from books.py

# Initialize app and db
app, db, _ = create_app()

with app.app_context():
    for book_data in all_books:
        # Avoid duplicates by checking the title
        if not Book.objects(title=book_data['title']):
            book = Book(
                title=book_data['title'],
                category=book_data.get('category', ''),
                genres=book_data.get('genres', []),
                description=book_data.get('description', []),
                authors=book_data.get('authors', []),
                pages=book_data.get('pages', 0),
                available=book_data.get('available', 0),
                copies=book_data.get('copies', 0),
                url=book_data.get('url', '')
            )
            book.save()
            print(f"Inserted: {book.title}")
        else:
            print(f"Already exists: {book_data['title']}")

    # Optional: print all books in DB
    print("\nBooks currently in DB:")
    for book in Book.objects:
        print(book.title, "-", book.category)

        # commen
