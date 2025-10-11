from flask import Blueprint, request, redirect, render_template, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import random

from app.models.loan import Loan
from app.models.book_doc import Book
from app.models.users import User

loan_bp = Blueprint('loanController', __name__)

# ============================================================
# MAKE A LOAN
# ============================================================

@loan_bp.route('/make_loan/<book_title>')
@login_required
def make_loan(book_title):

    # Check if user is admin
    if current_user.email == 'admin@lib.sg':
        flash('Admins cannot borrow books. This feature is for library members only.', 'warning')
        return redirect(url_for('packageController.book_titles'))
    
    # Get the book
    book = Book.get_book_by_title(book_title)
    
    if not book:
        flash(f'Book "{book_title}" not found.', 'danger')
        return redirect(url_for('packageController.book_titles'))
    
    # Generate random borrow date 10-20 days before today
    days_ago = random.randint(10, 20)
    borrow_date = datetime.now() - timedelta(days=days_ago)
    
    # Create the loan
    success, message, loan = Loan.create_loan(
        borrower=current_user._get_current_object(),
        book=book,
        borrow_date=borrow_date
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('packageController.book_titles'))


# ============================================================
# MANAGE LOANS (View all user's loans)
# ============================================================

@loan_bp.route('/my_loans')
@login_required
def my_loans():
    """
    Display all loans for the current user.
    """
    # Get all loans for current user
    all_loans = Loan.get_user_loans(current_user._get_current_object(), include_returned=True)
    
    return render_template('my_loans.html', panel="Current Loans", loans=all_loans)


# ============================================================
# RENEW LOAN
# ============================================================

@loan_bp.route('/renew_loan/<loan_id>', methods=['POST'])
@login_required
def renew_loan(loan_id):
    """
    Renew a loan for the current user.
    """
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    # Verify loan belongs to current user
    if loan.borrower.id != current_user.id:
        flash('You can only renew your own loans.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    success, message = loan.renew_loan()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('loanController.my_loans'))


# ============================================================
# RETURN LOAN
# ============================================================

@loan_bp.route('/return_loan/<loan_id>', methods=['POST'])
@login_required
def return_loan(loan_id):
    """
    Return a borrowed book.
    """
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    # Verify loan belongs to current user
    if loan.borrower.id != current_user.id:
        flash('You can only return your own loans.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    success, message = loan.return_loan()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('loanController.my_loans'))


# ============================================================
# DELETE LOAN
# ============================================================

@loan_bp.route('/delete_loan/<loan_id>', methods=['POST'])
@login_required
def delete_loan(loan_id):
    """
    Delete a returned loan record.
    """
    loan = Loan.get_loan_by_id(loan_id)
    
    if not loan:
        flash('Loan not found.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    # Verify loan belongs to current user
    if loan.borrower.id != current_user.id:
        flash('You can only delete your own loans.', 'danger')
        return redirect(url_for('loanController.my_loans'))
    
    success, message = loan.delete_loan()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('loanController.my_loans'))