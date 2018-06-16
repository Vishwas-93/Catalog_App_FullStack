from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, Items

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()


# Adds items to the Items class/ table in the Models
item1 = Items(item_name='Ball',
              item_description='Ball Ball Ball BallBall',
              cat_item_id='1', item_cat_name='Soccer')
session.add(item1)
session.commit()

item2 = Items(item_name='Ball Basket',
              item_description='Ball Ball Ball Basket Ball',
              cat_item_id='2', item_cat_name='Basketball')
session.add(item2)
session.commit()

item3 = Items(item_name='Bat',
              item_description='Bat Bat Bat Bat',
              cat_item_id='3', item_cat_name='Baseball')
session.add(item3)
session.commit()

item4 = Items(item_name='Frisbee disc',
              item_description='disc disc disc disc Fisbee',
              cat_item_id='4', item_cat_name='Frisbee')
session.add(item4)
session.commit()

item5 = Items(item_name='Snoboarding board',
              item_description='board boardboard board Snoboarding',
              cat_item_id='5', item_cat_name='Snoboarding')
session.add(item5)
session.commit()
