# Q2b/models/book_doc.py
from mongoengine import Document, StringField, ListField, IntField
from app.models.books import all_books

class Book(Document):
    meta = {"collection": "books"}

    # Fields
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
        """First + last paragraph joined."""
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
        """Populate MongoDB books collection once from all_books."""
        if cls.objects.count() > 0:
            return  # already seeded
        
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