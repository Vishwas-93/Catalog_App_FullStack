from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Category, Items, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/'
                     'profile_images/2671170543/'
                     '18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

category1 = Category(cat_name='Soccer', user_id=1)
session.add(category1)
session.commit()

item1 = Items(item_name='Ball',
              item_description='Ball Ball Ball BallBall',
              cat_item_id='1', item_cat_name='Soccer', user_id=1)
session.add(item1)
session.commit()


category2 = Category(cat_name='Basketball', user_id=1)
session.add(category2)
session.commit()


item2 = Items(item_name='Ball Basket',
              item_description='Ball Ball Ball Basket Ball',
              cat_item_id='2', item_cat_name='Basketball', user_id=1)
session.add(item2)
session.commit()

category3 = Category(cat_name='Baseball', user_id=1)
session.add(category3)
session.commit()

item3 = Items(item_name='Bat',
              item_description='Bat Bat Bat Bat', cat_item_id='3',
              item_cat_name='Baseball', user_id=1)
session.add(item3)
session.commit()


category4 = Category(cat_name='Frisbee', user_id=1)
session.add(category4)
session.commit()

item4 = Items(item_name='Frisbee disc',
              item_description='disc disc disc disc Fisbee',
              cat_item_id='4', item_cat_name='Frisbee', user_id=1)
session.add(item4)
session.commit()


category5 = Category(cat_name='Snoboarding', user_id=1)
session.add(category5)
session.commit()

item5 = Items(item_name='Snoboarding board',
              item_description='board boardboard board Snoboarding',
              cat_item_id='5', item_cat_name='Snoboarding', user_id=1)
session.add(item5)
session.commit()

print('Added all categories')
