##############################################################################
# Book Catalog database setup                                                #
# Written by Daniel McVicker                                                 #
# danielmcvicker@gmail.com                                                   #
# last update 11/27/2015                                                     #
# Running this file will set up the neccessary database and class            #
# definitions to run the book catalog project.                               #
# tested with sqlite 3 and sqlalchemy 0.8.4 Other versions may not work.     #
##############################################################################


from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Binary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    image = Column(String(250), default="/static/blank_user.gif")

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'image': self.image,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    binding = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    books = relationship('Book', cascade='delete')
    # note that deleting categories will delete any contained books
    # this is not ideal as images will be orphaned on the file system

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'binding': self.binding,
            'id': self.id,
        }


class Book(Base):
    __tablename__ = 'book'

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    author = Column(String(80), nullable=False)
    isbn = Column(String(20))
    fiction = Column(Integer, nullable=True)
    # Need to declare fiction as a bool but bool not supported by sqlite.
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    published = Column(String(4), nullable=True)
    image = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'isbn': self.isbn,
            'fiction': self.fiction,
        }

engine = create_engine('sqlite:///bookcatalog.db')

Base.metadata.create_all(engine)
