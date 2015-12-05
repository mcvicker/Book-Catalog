##Book Catalog Project

###What is it?

Daniel McVicker's solution for Udacity Full-Stack Nanodegree project 3.

This is a book catalog that demonstrates basic CRUD (create, read, update, delete) functionality, along with some basic 
image handling, JSON and XML API endpoints, Oauth2 providers, csv parsing and some other concepts.

###Prerequisites

See the requirements.txt file for the modules and libraries I used. Note that this project has not been tested with any other
versions. You may wish to use vagrant to launch the project as it will simplify things considerably--see the directions in
the setup section below.

Note: You will need to set up a google developer's account as well as a facebook developer's account.
This project needs a Google books-enabled Server API key from Google to enable book import functionality. 
This project needs a client id and app secret from Google to enable Google login.
This project needs an app id and client secret from Facebook to enable Facebook login.

####Some notable modules that were used: 
* Flask 0.10.1
* Flask-SeaSurf 0.2.1
* Jinja2 2.7.2
* SQLAlchemy 0.8.4
* Werkzeug 0.9.4
* dict2xml 1.4
* html5lib 0.999
* httplib2 0.9.1
* itsdangerous 0.22
* jsonpatch 1.3
* jsonpointer 1.0
* oauth 1.0.1
* oauth2client 1.4.12
* simplejson 3.3.1
* unicodecsv 0.14.1

See the requirements.txt file for the full list. 

###Installation

Edit the following files with your API information from the prerequisites step.

    client_secrets.json

requires Google Web Client information.

    server_secret_key.json

requires a Google API server key.

    fb_client_secrets.json

requires facebook client secrets. 

More information can be found at https://developers.google.com and https://developers.facebook.com respectively.

To take a look at the project, run

    python setup.py

from the directory you are currently in.
Setup can take a long time as the database has to be instantiated and nearly 1000 entries 
must be imported. You can use the catalog by navigating to http://localhost:8000

Note that if your environment differs from the vagrant environment that this project is contained in, you will likely need to
run files in this sequence to install:

    python database_setup.py
    python importer.py

Again, setup can take a long time.

**To simplify setup, you may wish to install vagrant.** 

For a brief overview of installing vagrant, check here:

https://www.udacity.com/wiki/ud197/install-vagrant

Once you've installed vagrant, start a session with the vagrant machine by navigating to the \vagrant\tournament directory
(in git bash for Windows or your terminal program for Mac) and type the following commands:

    vagrant up

Once the machine comes up, start an ssh session by typing

    vagrant ssh

Once that is complete, navigate to the \fullstack\vagrant\catalog\ directory.

###Usage

Start the server by typing 
    
    python catalog.py 
    
You can use the catalog by navigating to http://localhost:8000
You can stop the catalog by pressing ctrl + c.

####API Endpoints:

You can get data in JSON or XML formats:

#####To return JSON/XML for a specific category with category_id.

    http:localhost:8000/category/<int:category_id>/books/JSON
    http:localhost:8000/category/<int:category_id>/books/XML

#####To return JSON/XML serialized information for a specific book in category_id with book_id.

    http:localhost:8000/category/<int:category_id>/books/<int:book_id>/JSON
    http:localhost:8000/category/<int:category_id>/books/<int:book_id>/XML

#####To return JSON/XML serialized information for all categories.

    http:localhost:8000/category/JSON
    http:localhost:8000/category/XML

###Sources

I have heavily used the classwork from Udacity, documentation from Flask, Jinja and the [unicodecsv module](https://pypi.python.org/pypi/unicodecsv/0.14.1). I based the bookshelf css code on this [demo]
(http://www.bootply.com/jme11/7h2JKXv40U)

Thanks for taking a look. 
