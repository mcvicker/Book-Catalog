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

# set up and configure application, upload loactaions and allowed upload locations. 
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
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

# check uploaded files for allowed file types
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# proof of concept upload functionality
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
# proof of concept show image functionality.    
@app.route('/images/<filename>')
def uploaded_file(filename):
    return render_template('uploadedFile.html', filename = filename)

# Create a state token to prevent request forgery.
# Storing it in the session for later validation.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)       
# Google Plus OAuth2 code

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # validate the state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        reponse = make_response(json.dumps(result.get('error')), 500)
        reponse.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return reponse
    # Verify that the access token is valid for this application.
    if result['issued_to'] != CLIENT_ID:
        reponse = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        print "Token's client ID does not match app's."
        return response
        
    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token' : credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params = params)
    data = answer.json()
    
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['image'] = data['picture']
    login_session['email'] = data['email']
    
    # see if user exists, if it doesn't, make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id            
    
    output = ''
    output +='<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['image']
    output +=' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                    'email'], image=login_session['image'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user
    
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

        
# DISCONNECT FUNCTIONS

@app.route('/gdisconnect')
def gdisconnect():
    # Only Disconnect a connected user
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not logged in.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
     
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['image']
        
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
        
    else:
        # The given token was invalid.
        
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response
        


        
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
  if 'username' not in login_session:
    return redirect('/login')
  if request.method == 'POST':
      newCategory = Category(binding = request.form['binding'],
      user_id=login_session['user_id'])
      session.add(newCategory)
      flash('New Category %s Successfully Created' % newCategory.binding)
      session.commit()
      return redirect(url_for('showCategory'))
  else:
      return render_template('newCategory.html')
      


#Edit a Category
@app.route('/category/<int:category_id>/edit/', methods = ['GET', 'POST'])
def editCategory(category_id):
  if 'username' not in login_session:
    return redirect('/login')
  editedCategory = session.query(Category).filter_by(id = category_id).one()
  if editedCategory.user_id == login_session.get('user_id'):
    if request.method == 'POST':
        if request.form['binding']:
            editedCategory.binding = request.form['binding']
            flash('Category Successfully Edited %s' % editedCategory.binding)
            return redirect(url_for('showCategory'))
    else:
        return render_template('editCategory.html', category = editedCategory)
  else:
        return '<script>window.alert("You do not have authorization to edit this page!");</script>'
        # need to update this to return back to category page after throwing up error. 


@app.route('/category/<int:category_id>/delete/', methods = ['GET', 'POST'])
def deleteCategory(category_id):
  categoryToDelete = session.query(Category).filter_by(id = category_id).one()
  if 'username' not in login_session:
    return redirect('/login')
  if categoryToDelete.user_id == login_session.get('user_id'):
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
  else:
    return '<script>window.alert("You do not have authorization to delete this page!");</script>'
    # need to update this to return back to category page after throwing up error. 
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/books/')

#will need to carefully consider how this works with/against the autoimporter functionality
def showBooks(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    books = session.query(Book).filter_by(category_id = category_id).all()
    try:
        creator = session.query(User).filter_by(id = category.user_id).one()
        print dir(creator)
    except:
    # a placeholder creator for all the imported books with no true creator.
    # may just want to change the importer to import items with UID 0 or 1.
        creator = User(name='imported', email='email', id='0')
    if creator.id == login_session.get('user_id'):
        return render_template('books.html', books = books, category = category)
    # private template needs ui facelift.
    else:
       return render_template('publicbooks.html', books = books, category = category, creator = creator)

# need to add image handling.
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
    output += book.description
    output += "<br>"
    output += str(book.price)
    output += "<br>"
    output += str(book.isbn)
    output += "<br>"
    output += str(book.fiction)
    output += "<br>"
    output += str(book.published)
    output += "<br>"
    output += str(book.image)
    """
        # Need to declare fiction as a bool but bool not supported by sqlite.
        category_id = Column(Integer,ForeignKey('category.id'))
        user_id = Column(Integer,ForeignKey('user.id'))
        user = relationship(User)
        published = Column(String(4), nullable = True)
        image = Column(Integer,ForeignKey('image.id'))
    """    
    return render_template('book.html', category = category, book = book)
    
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
        if request.files['file']:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                # we need to save a slightly different version of the path in the database.
                dbpath = path.replace("/vagrant/catalog","")
                editedBook.image = dbpath
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
        app.run(host = '0.0.0.0', port = 8000)
        
# 750608331471-bpfc200kk4s6cjm5om3njl828kp495jh.apps.googleusercontent.com client ID
# iDYxmsXFexv9KXUZ7OqE6k_z client secret