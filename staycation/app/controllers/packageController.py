from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for

from models.forms import BookForm
from models.books import all_books
from models.users import User
from models.package import Package

package = Blueprint('packageController', __name__)

@package.route('/')
@package.route("/BookTitles")
# def book_titles():
#    # all_books = Book.getAllBooks()
#     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

def book_titles():
    # Get category from query parameter (default = All)
    selected_category = request.args.get('category', 'All')

    # ✅ Filter by category if not 'All'
    if selected_category == 'All':
        filtered_books = all_books
    else:
        filtered_books = [b for b in all_books if b['category'] == selected_category]

    # ✅ Sort filtered books alphabetically by title
    sorted_books = sorted(filtered_books, key=lambda b: b['title'].lower())

    # ✅ Keep only the first and last paragraphs of description
    for book in sorted_books:
        desc_list = book.get('description', [])
        if len(desc_list) > 1:
            short_desc = f"{desc_list[0]}\n\n{desc_list[-1]}"
        elif desc_list:
            short_desc = desc_list[0]
        else:
            short_desc = "No description available."
        book['short_description'] = short_desc

    return render_template(
        'books.html',
        panel="BOOK TITLES",
        all_books=sorted_books,
        selected_category=selected_category
    )

    

@package.route("/viewBookDetail/<book_title>")
def viewBookDetail(book_title):
    # Find the book by title
    the_book = next((b for b in all_books if b['title'] == book_title), None)
    
    if not the_book:
        return render_template('error.html', message="Book not found."), 404

    return render_template(
        'bookDetail.html',
        panel="BOOK DETAIL",
        book=the_book
    )