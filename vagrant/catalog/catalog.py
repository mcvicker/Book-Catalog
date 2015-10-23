from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from werkzeug import secure_filename
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Book, User
from flask import session as login_session 
import random
import string
import os


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

APPLICATION_NAME = "Book Catalog"
UPLOAD_FOLDER = '/vagrant/catalog/static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Database and create database session
engine = create_engine('sqlite:///bookcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/testupload/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
            <input type=submit value=Upload>
    </form>
    '''
    
@app.route('/images/<filename>')
def uploaded_file(filename):
    return render_template('uploadedFile.html', filename = filename)
    
    
#JSON APIs to view Book Information
@app.route('/category/<int:category_id>/books/JSON')
def bookCategoryJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    books = session.query(Book).filter_by(category_id = category_id).all()
    return jsonify(BooksInCategory=[i.serialize for i in books])


@app.route('/category/<int:category_id>/books/<int:book_id>/JSON')
def menuItemJSON(category_id, book_id):
    book = session.query(Book).filter_by(id = book_id).one()
    return jsonify(book = book.serialize)

@app.route('/category/JSON')
def restaurantsJSON():
    categories = session.query(Category).all()
    return jsonify(categories = [r.serialize for r in categories])

@app.route('/')   
@app.route('/category/')
def showCategory():
        categories = session.query(Category).order_by(asc(Category.binding))
        return render_template('categories.html', categories = categories)
        """
        def showRestaurants():
  restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
  if 'username' not in login_session:
    return render_template('publicrestaurants.html', restaurants = restaurants)
  else:
    return render_template('restaurants.html', restaurants = restaurants)
        """

# create a new category
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
  #if 'username' not in login_session:
  #  return redirect('/login')
  if request.method == 'POST':
      newCategory = Category(binding = request.form['binding'])
      #, user_id=login_session['user_id']) commented out until login is set up
      session.add(newCategory)
      flash('New Category %s Successfully Created' % newCategory.binding)
      session.commit()
      return redirect(url_for('showCategory'))
  else:
      return render_template('newCategory.html')
      # need to set up templates for these


#Edit a Category
@app.route('/category/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
  #if 'username' not in login_session:
    #return redirect('/login')
  editedCategory = session.query(Category).filter_by(id = category_id).one()
  #if editedCategory.user_id == login_session.get('user_id'):
  if request.method == 'POST':
    if request.form['name']:
        editedCategory.binding = request.form['binding']
        flash('Category Successfully Edited %s' % editedCategory.binding)
        return redirect(url_for('showCategories'))
  else:
        return render_template('editCategory.html', category = editedCategory)
  #else:
        #return '<script>window.alert("You do not have authorization to edit this page!");</script>'


@app.route('/category/<int:category_id>/delete/', methods = ['GET', 'POST'])
def deleteCategory(category_id):
  categoryToDelete = session.query(Category).filter_by(id = category_id).one()
  #if 'username' not in login_session:
    #return redirect('/login')
  #if restaurantToDelete.user_id == login_session.get('user_id'):
  if request.method == 'POST':
    if 'delete' in request.form:
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.binding)
        session.commit()
        return redirect(url_for('showCategory', category_id = category_id))
    elif 'cancel' in request.form:
        flash ('Deletion of %s Canceled' % categoryToDelete.binding )
        return redirect(url_for('showCategory'))       
  else:
    return render_template('deleteCategory.html',category = categoryToDelete)
  #else:
    #return '<script>window.alert("You do not have authorization to delete this page!");</script>'

@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/books/')
def showBooks(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    books = session.query(Book).filter_by(category_id = category_id).all()
    # creator = session.query(User).filter_by(id = restaurant.user_id).one()
    #if restaurant.user_id == login_session.get('user_id'):
    return render_template('books.html', books = books, category = category)
    #else:
    #   return render_template('publicmenu.html', items = items, restaurant = restaurant, creator = creator)

# need to add isbn as an editable field
@app.route('/category/<int:category_id>/book/new/',methods=['GET','POST']) 
def newBook(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        newBook = Book(title = request.form['title'], author = request.form['author'], price = request.form['price'],
                       description = request.form['description'], fiction = request.form['fiction'], 
                       isbn = request.form['isbn'], published = request.form['published'], category_id = category_id)
        session.add(newBook)
        session.commit()
        flash('New Book %s Successfully Created' % (newBook.title))
        return redirect(url_for('showCategory', category_id = category_id))
    else:
            return render_template('newBook.html')
            


# prettify this -- use a template
@app.route('/category/<int:category_id>/book/<int:book_id>/')
def showBook(category_id, book_id):
    category = session.query(Category).filter_by(id = category_id).one()
    book = session.query(Book).filter_by(id = book_id).one()
    output = ""
    output += book.title
    output += "<br>"
    output += book.author
    output += "<br>"
    output += str(book.id)
    output += "<br>"
    output += str(book.description)
    output += "<br>"
    output += str(book.price)
    output += "<br>"
    output += str(book.isbn)
    output += "<br>"
    output += str(book.fiction)
    output += "<br>"
    output += str(book.published)
    output += "<br>"
    output += book.picture
    """
        # Need to declare fiction as a bool but bool not supported by sqlite.
        category_id = Column(Integer,ForeignKey('category.id'))
        user_id = Column(Integer,ForeignKey('user.id'))
        user = relationship(User)
        published = Column(String(4), nullable = True)
        image = Column(Integer,ForeignKey('image.id'))
    """    
    return output
    
@app.route('/category/<int:category_id>/book/<int:book_id>/edit/', methods=['GET', 'POST'])    
def editBook(category_id, book_id):
    category = session.query(Category).filter_by(id = category_id).one()
    editedBook = session.query(Book).filter_by(id = book_id).one()
    if request.method == 'POST':
        if request.form['title']:
            editedBook.title = request.form['title']
        if request.form['description']:
            editedBook.description = request.form['description']
        if request.form['price']:
            editedBook.price = request.form['price']
        if request.form['fiction']:
            editedBook.fiction = request.form['fiction']
        if request.form['author']:
            editedBook.author = request.form['author']
        if request.form['isbn']:
            editedBook.isbn = request.form['isbn']
        if request.form['published']:
            editedBook.published = request.form['published']
        session.add(editedBook)
        session.commit() 
        flash('Book Successfully Edited')
        return redirect(url_for('showCategory'))
    else:
        return render_template('editBook.html', category_id = category_id, book_id = book_id, book = editedBook)
    
@app.route('/category/<int:category_id>/books/<int:book_id>/delete/', methods=['GET', 'POST'])
def deleteBook(category_id, book_id):
    category = session.query(Category).filter_by(id = category_id).one()
    bookToDelete = session.query(Book).filter_by(id = book_id).one()
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash ('Book Successfully Deleted')
        return redirect(url_for('showBooks', category_id = category_id))
    else:
        return render_template('deleteBook.html', book = bookToDelete, category_id = category_id)
   
if __name__ == '__main__':
        app.debug = True
        app.secret_key = 'mr_bigglesworth'
        app.run(host = '0.0.0.0', port = 5000)