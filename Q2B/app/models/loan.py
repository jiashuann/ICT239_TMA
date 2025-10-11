from mongoengine import Document, ReferenceField, DateTimeField, IntField, BooleanField
from datetime import datetime
from app.models.users import User
from app.models.book_doc import Book

class Loan(Document):
    """
    Loan model to track book borrowing by users.
    
    Fields:
    - borrower: Reference to User who borrowed the book
    - book: Reference to Book being borrowed
    - borrow_date: Date when book was borrowed
    - return_date: Date when book was returned (None if not yet returned)
    - renew_count: Number of times loan has been renewed
    """
    
    meta = {'collection': 'loans'}
    
    borrower = ReferenceField(User, required=True)
    book = ReferenceField(Book, required=True)
    borrow_date = DateTimeField(required=True)
    return_date = DateTimeField(default=None)
    renew_count = IntField(default=0)
    
    # ============================================================
    # CREATE LOAN
    # ============================================================
    
    @staticmethod
    def create_loan(borrower, book, borrow_date):
        """
        Create a new loan for a user.
        
        Args:
            borrower (User): User making the loan
            book (Book): Book being borrowed
            borrow_date (datetime): Date of borrowing
        
        Returns:
            tuple: (success: bool, message: str, loan: Loan or None)
        
        Business Rules:
        - User cannot have multiple unreturned loans for the same book
        - Book must have available copies (available > 0)
        - Updates book's available count upon successful loan
        """
        # Check if book has available copies
        if book.available <= 0:
            return False, f"Cannot create loan. '{book.title}' has no available copies.", None
        
        # Check if user already has an unreturned loan for this book
        existing_loan = Loan.objects(
            borrower=borrower,
            book=book,
            return_date=None  # Unreturned loans have return_date = None
        ).first()
        
        if existing_loan:
            return False, f"You already have an unreturned loan for '{book.title}'.", None
        
        # Create the loan
        loan = Loan(
            borrower=borrower,
            book=book,
            borrow_date=borrow_date,
            return_date=None,
            renew_count=0
        )
        loan.save()
        
        # Update book's available count
        success, message = book.borrow_book()
        if not success:
            # Rollback: delete the loan if book update fails
            loan.delete()
            return False, message, None
        
        return True, f"Successfully borrowed '{book.title}'.", loan
    
    # ============================================================
    # RETRIEVE LOANS
    # ============================================================
    
    @staticmethod
    def get_user_loans(borrower, include_returned=True):
        """
        Retrieve all loans for a specific user.
        
        Args:
            borrower (User): User whose loans to retrieve
            include_returned (bool): If False, only returns unreturned loans
        
        Returns:
            QuerySet: List of Loan objects
        """
        if include_returned:
            return Loan.objects(borrower=borrower).order_by('-borrow_date')
        else:
            return Loan.objects(borrower=borrower, return_date=None).order_by('-borrow_date')
    
    @staticmethod
    def get_loan_by_id(loan_id):
        """
        Retrieve a specific loan by its ID.
        
        Args:
            loan_id (str): Loan document ID
        
        Returns:
            Loan or None
        """
        return Loan.objects(id=loan_id).first()
    
    @staticmethod
    def get_specific_loan(borrower, book, unreturned_only=True):
        """
        Retrieve a specific loan for a user and book.
        
        Args:
            borrower (User): User who borrowed
            book (Book): Book borrowed
            unreturned_only (bool): If True, only returns unreturned loans
        
        Returns:
            Loan or None
        """
        if unreturned_only:
            return Loan.objects(borrower=borrower, book=book, return_date=None).first()
        else:
            return Loan.objects(borrower=borrower, book=book).order_by('-borrow_date').first()
    
    # ============================================================
    # UPDATE LOAN - RENEW
    # ============================================================
    
    def renew_loan(self, new_borrow_date=None):
        """
        Renew a loan by updating the borrow date and incrementing renew count.
        
        Args:
            new_borrow_date (datetime): New borrow date (defaults to today)
        
        Returns:
            tuple: (success: bool, message: str)
        
        Business Rules:
        - Can only renew unreturned loans (return_date must be None)
        - Increments renew_count by 1
        - Updates borrow_date to extend the loan period
        """
        if self.return_date is not None:
            return False, f"Cannot renew. This loan has already been returned on {self.return_date.strftime('%d/%m/%Y')}."
        
        if new_borrow_date is None:
            new_borrow_date = datetime.now()
        
        self.borrow_date = new_borrow_date
        self.renew_count += 1
        self.save()
        
        return True, f"Successfully renewed '{self.book.title}'. Renewal count: {self.renew_count}."
    
    # ============================================================
    # UPDATE LOAN - RETURN
    # ============================================================
    
    def return_loan(self, return_date=None):
        """
        Return a borrowed book by setting the return date.
        
        Args:
            return_date (datetime): Date of return (defaults to today)
        
        Returns:
            tuple: (success: bool, message: str)
        
        Business Rules:
        - Can only return unreturned loans (return_date must be None)
        - Updates book's available count
        - Sets return_date to mark loan as completed
        """
        if self.return_date is not None:
            return False, f"This loan has already been returned on {self.return_date.strftime('%d/%m/%Y')}."
        
        if return_date is None:
            return_date = datetime.now()
        
        # Update book's available count
        success, message = self.book.return_book()
        if not success:
            return False, f"Failed to update book availability: {message}"
        
        # Mark loan as returned
        self.return_date = return_date
        self.save()
        
        return True, f"Successfully returned '{self.book.title}'."
    
    # ============================================================
    # DELETE LOAN
    # ============================================================
    
    def delete_loan(self):
        """
        Delete a loan record.
        
        Returns:
            tuple: (success: bool, message: str)
        
        Business Rules:
        - Can only delete returned loans (return_date must not be None)
        - Prevents deletion of active loans
        """
        if self.return_date is None:
            return False, f"Cannot delete an unreturned loan. Please return '{self.book.title}' first."
        
        book_title = self.book.title
        self.delete()
        
        return True, f"Successfully deleted loan record for '{book_title}'."
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def is_returned(self):
        """
        Check if loan has been returned.
        
        Returns:
            bool: True if returned, False otherwise
        """
        return self.return_date is not None
    
    def is_overdue(self, due_days=14):
        """
        Check if loan is overdue.
        
        Args:
            due_days (int): Number of days before loan is due (default 14)
        
        Returns:
            bool: True if overdue, False otherwise
        """
        if self.return_date is not None:
            return False  # Already returned
        
        from datetime import timedelta
        due_date = self.borrow_date + timedelta(days=due_days)
        return datetime.now() > due_date
    
    def days_borrowed(self):
        """
        Calculate how many days the book has been borrowed.
        
        Returns:
            int: Number of days
        """
        if self.return_date is not None:
            return (self.return_date - self.borrow_date).days
        else:
            return (datetime.now() - self.borrow_date).days
    
    def get_due_date(self, due_days=14):
        """
        Calculate the due date for the loan.
        
        Args:
            due_days (int): Number of days before loan is due (default 14)
        
        Returns:
            datetime: Due date
        """
        from datetime import timedelta
        return self.borrow_date + timedelta(days=due_days)
    
    @staticmethod
    def get_all_overdue_loans(due_days=14):
        """
        Retrieve all overdue unreturned loans.
        
        Args:
            due_days (int): Number of days before loan is due (default 14)
        
        Returns:
            list: List of overdue Loan objects
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=due_days)
        
        return Loan.objects(
            return_date=None,
            borrow_date__lt=cutoff_date
        )