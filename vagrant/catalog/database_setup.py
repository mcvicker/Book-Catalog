from sqlalchemy import Column, ForeignKey, Integer, String, Binary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# sqlite 3
# sqlalchemy 0.8.4

Base = declarative_base()

class User(Base):
        __tablename__ = 'user'
        
        id = Column(Integer, primary_key=True)
        name = Column(String(250), nullable=False)
        email = Column(String(250), nullable=False)
        picture = Column(String(250))
        
        @property
        def serialize(self):
            """Return object data in easily serializable format"""
            return {
                'id'        : self.id,
                'name'      : self.name,
                'email'     : self.email,
                'picture'   : self.picture,
                }
            
class Category(Base):
        __tablename__ = 'category'
        
        id = Column(Integer, primary_key=True)
        binding = Column(String(250), nullable=False)
        user_id = Column(Integer,ForeignKey('user.id'))
        user = relationship(User)
                
        
        @property
        def serialize(self):
            """Return object data in easily serializable format"""
            return {
                'binding'      : self.binding,
                'id'        : self.id,
                }
                
class Image(Base):
        __tablename__ = 'image'
        
        name = Column(String(80), nullable = False)
        id = Column(Integer, primary_key = True)
        blob = Column(Binary)
        
        
class Book(Base):
        __tablename__ = 'book'
        
        title =  Column(String(80), nullable = False)
        id = Column(Integer, primary_key = True)
        description = Column(String(250))
        price = Column(String(8))
        author = Column(String(80), nullable = False)
        isbn = Column(String(20))
        fiction = Column(Integer, nullable = True)
        # Need to declare fiction as a bool but bool not supported by sqlite.
        category_id = Column(Integer,ForeignKey('category.id'))
        user_id = Column(Integer,ForeignKey('user.id'))
        user = relationship(User)
        published = Column(String(4), nullable = True)
        image = Column(Integer,ForeignKey('image.id'))
        

        
        @property
        def serialize(self):
            """Return object data in easily serializable format"""
            return {
            'title'     : self.title,
            'description'   : self.description,
            'id'        : self.id,
            'price'     : self.price,
            'isbn'      : self.isbn,
            'fiction'   : self.fiction,
            }
            
engine = create_engine('sqlite:///bookcatalog.db')

Base.metadata.create_all(engine)
        
        