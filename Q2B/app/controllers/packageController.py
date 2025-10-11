from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash

from app.models.forms import BookForm, AddBookForm
from app.models.books import all_books
from app.models.users import User
from app.models.package import Package

#mongoDB
from app.models.book_doc import Book

package = Blueprint('packageController', __name__)


@package.route('/')
@package.route("/BookTitles")
# def book_titles():
#    # all_books = Book.getAllBooks()
#     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

def book_titles():
    # Seed MongoDB if empty (first time only)
    Book.seed_from_all_books_if_empty()
    
    selected_category = request.args.get('category', 'All')

    # Query MongoDB instead of all_books list
    if selected_category == 'All':
        books_query = Book.objects()
    else:
        books_query = Book.objects(category=selected_category)
    
    # Sort alphabetically by title using MongoDB
    sorted_books = books_query.order_by('title')

    return render_template('books.html', panel="BOOK TITLES", 
                         all_books=sorted_books, 
                         selected_category=selected_category)
    

@package.route("/viewBookDetail/<book_title>")
def viewBookDetail(book_title):
    # Query MongoDB for the book
    the_book = Book.objects(title=book_title).first()
    
    if not the_book:
        return render_template('error.html', message="Book not found."), 404

    return render_template('bookDetails.html', panel="BOOK DETAILS", book=the_book)

@package.route('/newBook', methods=['GET', 'POST'])
@login_required
def newBook():
    # Check if user is admin
    if current_user.email != 'admin@lib.sg':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('packageController.book_titles'))
    
    form = AddBookForm()
    
    # Get number of author fields (default 1, max 20)
    num_authors = int(request.form.get('num_authors', 1))
    
    if request.method == 'POST':
        # Check if user clicked "Add Another Author"
        if 'add_author' in request.form:
            num_authors += 1
            form.process(formdata=request.form)
            return render_template('addBook.html', panel="ADD A BOOK", form=form, num_authors=num_authors)
        
        # Check if user clicked "Remove Last Author"
        if 'remove_author' in request.form and num_authors > 1:
            num_authors -= 1
            form.process(formdata=request.form)
            return render_template('addBook.html', panel="ADD A BOOK", form=form, num_authors=num_authors)
        
        # Final submit - validate and save
        if form.validate_on_submit() or request.form.get('title'):  # Basic validation
            # Collect genres from checkboxes (not from form field)
            selected_genres = request.form.getlist('genres')
            
            # Collect authors from form
            authors = []
            for i in range(1, num_authors + 1):
                author_name = request.form.get(f'author_{i}', '').strip()
                is_illustrator = request.form.get(f'illustrator_{i}')
                
                if author_name:
                    if is_illustrator:
                        authors.append(f"{author_name} (Illustrator)")
                    else:
                        authors.append(author_name)
            
            # Split description by double newlines to create paragraphs
            description_text = form.description.data or ""
            description_list = [p.strip() for p in description_text.split('\n\n') if p.strip()]
            
            # Validate required fields
            if not form.title.data:
                flash('Title is required!', 'danger')
                return render_template('addBook.html', panel="ADD A BOOK", form=form, num_authors=num_authors)
            
            if not selected_genres:
                flash('Please select at least one genre!', 'danger')
                return render_template('addBook.html', panel="ADD A BOOK", form=form, num_authors=num_authors)
            
            # Create new book
            new_book = Book(
                title=form.title.data,
                category=form.category.data,
                genres=selected_genres,  # Use checkbox selections
                url=form.url.data or "",
                description=description_list,
                authors=authors,
                pages=form.pages.data or 0,
                available=form.copies.data or 0,
                copies=form.copies.data or 0
            )
            
            new_book.save()
            flash('Book added successfully!', 'success')
            return redirect(url_for('packageController.book_titles'))
    
    return render_template('addBook.html', panel="ADD A BOOK", form=form, num_authors=num_authors)