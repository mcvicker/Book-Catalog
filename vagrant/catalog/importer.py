import unicodecsv as csv
# uses unicodecsv package because built-in csv package in python does not 
# support unicode, which is needed for the database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import User, Base, Category, Book
 
import httplib2
import json

engine = create_engine('sqlite:///bookcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

    
# we open up the .tsv file to get a selection of books.
allbindings = []
with open('My_Shelfari_Books.tsv','rb') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter=',')
    #print reader.fieldnames
    for row in reader:
        allbindings.append(row['Binding'])
        
bindings = set(allbindings)
for item in bindings:
    category = Category(binding = item)
    session.add(category)
    session.commit()
# we put the bindings in place first so that we can connect the books to binding types in the next step
    
with open('My_Shelfari_Books.tsv','rb') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter=',')        
    for row in reader:    
        title = (row)['Title']
        author = (row)['Author']
        isbn = (row)['ISBN']
        published = (row)['Year Published']
        binding = (row)['Binding']
        token = title.replace(" ", "+")
        # we look at the binding type to determine the category
        category = session.query(Category).filter_by(binding = binding).one()
        # we pull down a description from google books
        # will need to pull the first result out of the api.
        url = 'https://www.googleapis.com/books/v1/volumes?q=%s&fields=items(volumeInfo/description)&key=AIzaSyDalhBzXGHjJYN6rW-ry-KbjM9kbcdR6o0' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)
        description = data["items"][0]['volumeInfo']['description']
        book = Book(
            title = title, author = author, isbn = isbn, published = published, 
            category_id = category.id, description = description)
        session.add(book)
        session.commit()
        print title + " imported..."
        # need to build error message for exceeding the limit
        
    
