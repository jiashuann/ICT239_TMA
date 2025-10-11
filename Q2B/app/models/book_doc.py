from mongoengine import Document, StringField, ListField, IntField
from app.models.books import all_books

class Book(Document):
    meta = {"collection": "books"}

    # Fields matching the database schema
    title = StringField(required=True, unique=True, max_length=300)
    category = StringField()
    url = StringField()
    description = ListField(StringField())
    authors = ListField(StringField())
    genres = ListField(StringField())
    pages = IntField()
    available = IntField()
    copies = IntField()

    @property
    def short_description(self):
        """Returns first and last paragraph of description."""
        if not self.description:
            return ""
        parts = [p.strip() for p in self.description if p and p.strip()]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        return f"{parts[0]} ... {parts[-1]}"

    @classmethod
    def seed_from_all_books_if_empty(cls):
        """Populate MongoDB from all_books if collection is empty."""
        if cls.objects.count() > 0:
            return  # Already seeded
        
        docs = []
        for b in all_books:
            docs.append(cls(
                title=b["title"],
                category=b.get("category", ""),
                url=b.get("url", ""),
                description=b.get("description", []),
                authors=b.get("authors", []),
                genres=b.get("genres", []),
                pages=b.get("pages", 0),
                available=b.get("available", 0),
                copies=b.get("copies", 0),
            ))
        if docs:
            cls.objects.insert(docs, load_bulk=False)

    # ============================================================
    # NEW METHODS FOR BORROWING AND RETURNING BOOKS
    # ============================================================
    
    def borrow_book(self):
        """
        Borrow a book (decrease available count by 1).
        
        Returns:
            tuple: (success: bool, message: str)
        
        Sanity checks:
        - Book must have at least 1 available copy
        - Available count cannot go below 0
        """
        if self.available <= 0:
            return False, f"Cannot borrow '{self.title}'. No copies available."
        
        if self.available > self.copies:
            return False, f"Data error: Available copies ({self.available}) exceeds total copies ({self.copies})."
        
        # Decrease available count
        self.available -= 1
        self.save()
        
        return True, f"Successfully borrowed '{self.title}'. {self.available} copies remaining."
    
    def return_book(self):
        """
        Return a borrowed book (increase available count by 1).
        
        Returns:
            tuple: (success: bool, message: str)
        
        Sanity checks:
        - Available count cannot exceed total copies
        - Book must have been previously borrowed (available < copies)
        """
        if self.available >= self.copies:
            return False, f"Cannot return '{self.title}'. All {self.copies} copies are already available (none borrowed)."
        
        if self.available < 0:
            return False, f"Data error: Available count ({self.available}) is negative."
        
        # Increase available count
        self.available += 1
        self.save()
        
        return True, f"Successfully returned '{self.title}'. {self.available} of {self.copies} copies now available."
    
    @staticmethod
    def get_book_by_title(title):
        """
        Retrieve a book by its title.
        
        Args:
            title (str): The book title
        
        Returns:
            Book object or None
        """
        return Book.objects(title=title).first()
    
    def is_available(self):
        """
        Check if book has available copies.
        
        Returns:
            bool: True if available > 0, False otherwise
        """
        return self.available > 0
    
    def get_borrowed_count(self):
        """
        Calculate how many copies are currently borrowed.
        
        Returns:
            int: Number of borrowed copies
        """
        return self.copies - self.available