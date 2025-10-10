from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for

from app.models.forms import BookForm
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