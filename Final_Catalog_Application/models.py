from sqlalchemy import Column, table, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()


class User(Base):
    '''This class stores the details of the registered user'''
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(40), nullable=False)
    picture = Column(String(250))


class Category(Base):
    '''This class stores the categories in the catalog'''
    __tablename__ = 'category'
    cat_id = Column(Integer, primary_key=True)
    cat_name = Column(String(40))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


class Items(Base):
    ''' This class stores the items in each category '''
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True)
    item_name = Column(String(40))
    item_description = Column(String(40))
    item_cat_name = Column(String(40))
    cat_item_id = Column(Integer, ForeignKey('category.cat_id'))
    category = relationship(Category)
    date_time = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # This is used to return data in the form of JSON array
    @property
    def Serialize(self):
        return {
            'category': self.item_cat_name,
            'category_id': self.cat_item_id,
            'item': self.item_name,
            'item_description': self.item_description,
            'item_id': self.item_id,
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
