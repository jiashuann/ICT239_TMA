from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, FloatField, TextAreaField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import Email, Length, InputRequired, input_required, Optional

class RegForm(FlaskForm):
    email = StringField('Email',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=20)])
    name = StringField('Name')

class BookForm(FlaskForm):
    check_in_date = DateTimeField('check_in_date',  validators=[InputRequired()])

# NEW: Add Book Form
class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=300)])
    category = SelectField('Choose a category', 
                          choices=[('Children', 'Children'), 
                                   ('Teens', 'Teens'), 
                                   ('Adult', 'Adult')],
                          validators=[InputRequired()])
    genres = SelectMultipleField('Choose multiple Genres',
                                 choices=[
                                     ('Animals', 'Animals'),
                                     ('Biography', 'Biography'),
                                     ('Biography Memoir', 'Biography Memoir'),
                                     ('BookClub', 'BookClub'),
                                     ('Business', 'Business'),
                                     ('Classics', 'Classics'),
                                     ('Comics', 'Comics'),
                                     ('Communication', 'Communication'),
                                     ('Contemporary', 'Contemporary'),
                                     ('Dark Academia', 'Dark Academia'),
                                     ('Emotion', 'Emotion'),
                                     ('Fantasy', 'Fantasy'),
                                     ('Fiction', 'Fiction'),
                                     ('Friendship', 'Friendship'),
                                     ('Graphic Novels', 'Graphic Novels'),
                                     ('Grief', 'Grief'),
                                     ('Historical Fiction', 'Historical Fiction'),
                                     ('Indigenous', 'Indigenous'),
                                     ('Inspirational', 'Inspirational'),
                                     ('Leadership', 'Leadership'),
                                     ('Magic', 'Magic'),
                                     ('Memoir', 'Memoir'),
                                     ('Mental Health', 'Mental Health'),
                                     ('Nonfiction', 'Nonfiction'),
                                     ('Personal Development', 'Personal Development'),
                                     ('Picture Books', 'Picture Books'),
                                     ('Poetry', 'Poetry'),
                                     ('Productivity', 'Productivity'),
                                     ('Psychology', 'Psychology'),
                                     ('Romance', 'Romance'),
                                     ('School', 'School'),
                                     ('Self Help', 'Self Help'),
                                     ('Thriller', 'Thriller')
                                 ])
    url = StringField('URL for Cover', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    
    # Authors and illustrator checkboxes
    author1 = StringField('Author 1', validators=[Optional()])
    illustrator1 = BooleanField('Illustrator')
    author2 = StringField('Author 2', validators=[Optional()])
    illustrator2 = BooleanField('Illustrator')
    author3 = StringField('Author 3', validators=[Optional()])
    illustrator3 = BooleanField('Illustrator')
    author4 = StringField('Author 4', validators=[Optional()])
    illustrator4 = BooleanField('Illustrator')
    author5 = StringField('Author 5', validators=[Optional()])
    illustrator5 = BooleanField('Illustrator')
    
    pages = IntegerField('Number of pages', validators=[Optional()])
    copies = IntegerField('Number of copies', validators=[Optional()])