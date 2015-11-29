##############################################################################
# Book Catalog Importer                                                      #
# Written by Daniel McVicker                                                 #
# danielmcvicker@gmail.com                                                   #
# last update 11/22/2015                                                     #
# importer.py imports books from a Shelfari TSV file.                        #
# based on the book's title, it finds each book  using google books API      #
# and finds an appropriate image and description for each book.              #
# It imports the fields from the TSV and the API into the bookcatalog.db     #
# Note that you can't run this importer indefinitely, google has             #
# daily data caps.                                                           #
##############################################################################

from __future__ import division
# imported to give reasonable division
from decimal import *
# imported to give sensible progress status as the import happens.


import unicodecsv as csv
# uses unicodecsv package because built-in csv package in python does not
# support unicode, which is needed for the database

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Base, Category, Book


import httplib2
import json
# in order to grab descriptions from google books api

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

# first, set up an 'imported' user
imported = User(name='Automatically Imported',
                email='automaticimport@noreply.com',
                id='0', image="/static/automatic-import.jpg")
session.add(imported)
session.commit()

# we open up the .tsv file to get a selection of bindings.
# this also sets an allrows variable to get the number of rows later.

allrows = []
with open('My_Shelfari_Books.tsv', 'rb') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter=',')
    # Blank bindings are confusing so we remove them in this step.
    for row in reader:
        if row['Binding'] == '':
            allrows.append('Unknown Binding')
        else:
            allrows.append(row['Binding'])


bindings = set(allrows)

# we put the bindings in place first so that we can connect the books to
# binding types in the next step
for index, item in enumerate(bindings, start=1):
    category = Category(binding=item, user_id='0')
    session.add(category)
    session.commit()
    completed = Decimal(index / len(bindings) * 100).quantize(Decimal('.01'))
    MessageOne = " imported... Stage One of Two "
    MessageTwo = "% complete"
    print item + MessageOne + str(completed) + MessageTwo

# I don't believe that this import process is optimized.
# Likely there is a better way to batch web requests to google as well as
# database writes. Potentially read everything into python variables and
# then do a massive write to the database? Maybe do sets of 10 or 100?
# Also, returning just the first result is not always correct.
# A number of Richard Stark books are coming up wrong.


with open('My_Shelfari_Books.tsv', 'rb') as tsvfile:
    reader = csv.DictReader(tsvfile, delimiter=',')
    # start our count at 1 to create meaningful progress status.
    key = "AIzaSyDalhBzXGHjJYN6rW-ry-KbjM9kbcdR6o0"
    # our access key for the google books API
    for index, row in enumerate(reader, start=1):
        title = (row)['Title']
        author = (row)['Author']
        isbn = (row)['ISBN']
        published = (row)['Year Published']
        # again, we shouldn't import a blank binding type
        if (row)['Binding'] != '':
            binding = (row)['Binding']
        else:
            binding = 'Unknown Binding'
        user_id = '0'
        token = title.replace(" ", "+")
        # we look at the binding type to determine the category
        category = session.query(Category).filter_by(binding=binding).one()
        # we pull down a description from google books
        # will need to pull the first result out of the api.
        url = ('https://www.googleapis.com/books/v1/'
               'volumes?q=%s&fields=items(volumeInfo/description)'
               ',items(volumeInfo/imageLinks)&key=%s') % (token, key)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)
        # if our data doesn't exist, we can't import it.
        try:
            description = data["items"][0]['volumeInfo']['description']
        except:
            description = ""
        try:
            image = data["items"][0]['volumeInfo']['imageLinks']['thumbnail']
        except:
            image = ""
        book = Book(
            title=title, author=author, isbn=isbn, published=published,
            category_id=category.id, description=description,
            image=image, user_id=user_id)
        session.add(book)
        session.commit()
        # we reuse the allrows variable to determine the percentage completed
        completed = Decimal(index / len(allrows) *
                            100).quantize(Decimal('.01'))
        MessageOne = " imported... Stage Two of Two "
        MessageTwo = "% complete"
        print "\"" + title + "\"" + MessageOne + str(completed) + MessageTwo
