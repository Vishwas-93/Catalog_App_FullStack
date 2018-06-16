from flask import Flask, request, url_for, g, jsonify, \
    render_template, redirect, make_response, json, abort
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Category, Items, Base, User
from flask import session as login_session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

# Read the client Id from the client_secrets.json downloaded from the
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Final Project"


engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


app = Flask(__name__)


# Route for the Login
@app.route('/login')
def showLogin():
    state = ''.join(random.
                    choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print(login_session['state'])
    return render_template('login.html', STATE=state)


# Route for google API Connect
@app.route('/googleConnect', methods=['POST'])
def googleConnect():
    # Check if the user requesting the resource is the one who is intended to
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
        print("Inside oauth")
        # credentials = json.dumps(credentials)

        print('Credentials id token %s' % credentials.id_token)
        # credentials.to_json()
        # print(credentials)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if the token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print('Result %s' % result)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print("Inside Error!!")
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print('gplus_id %s' % gplus_id)
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    print("Login Session 1 %s" % login_session)
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    print(stored_gplus_id)
    print(gplus_id)
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        print("Inside current user already connected")
        response = make_response(json.dumps
                                 ("Current user is already connected."),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)
    login_session['provider'] = 'google_plus'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    print("Login session %s" % login_session)
    print("Email %s" % login_session['email'])

    user_id = getuserid(login_session['email'])
    print(user_id)
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    # flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# Route to disconnect
@app.route('/disgconnect')
def disgconnect():
    credentials = login_session.get('credentials')
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current User Not Connected'))
        response.headers['content-Type'] = 'application/json'
        return response

    print("In gdisconnect and the current access token is %s" % access_token)
    print("User Name is :")
    print(login_session['username'])
    url = \
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % login_session['access_token']
    print(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('Result is:')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        response = make_response(json.dumps('Successfully Disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        print("After delete" % login_session)
        return redirect(url_for('getAllCategories'))
    else:
        response = \
            make_response(json.dumps('Failed to revoke token for given user'),
                          400)
        response.headers['Content-Type'] = 'application/json'
        return response
        # return response


def getuserid(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        print("Inside get User Id method %s" % user)
        user_id = user.id
        return user_id
    except:
        return None


def getuserinfo(user_id):
    userinfo = session.query(User).filter_by(id=user_id).one()
    return userinfo


def createUser(login_session):
    user_to_add = User(name=login_session['username'],
                       email=login_session['email'],
                       picture=login_session['picture'])
    session.add(user_to_add)
    session.commit()
    return user_to_add.id


# Route to landing page
@app.route('/', methods=['GET'])
def getAllCategories():
    categories = session.query(Category).all()
    items = session.query(Items).order_by(desc(Items.date_time)).limit(3).all()
    if 'username' not in login_session:
        user_logged_in = False
    else:
        user_logged_in = True
    return render_template('catalog.html',
                           categories=categories, items=items,
                           user_logged_in=user_logged_in)


# Route to the items page of an individual category
@app.route('/catalog/<category>/items', methods=['GET', 'POST'])
def getItems(category):
    if request.method == 'GET':
        categories = session.query(Category).all()
        items = session.query(Items).filter_by(item_cat_name=category).all()
        number_of_items = len(items)
        # Create a dictionary to get the count and category for All Categories
        dict_cat = {}
        print(len(categories))
        print(categories[5].cat_name)
        item_cat_cric = session.query(Items).\
            filter_by(item_cat_name=categories[5].cat_name).all()
        for i in range(0, len(categories)):
            item_cat = session.query(Items).\
                filter_by(item_cat_name=categories[i].cat_name).all()
            if len(item_cat) == 0:
                dict_cat[categories[i].cat_name] = "0"
            else:
                dict_cat[categories[i].cat_name] = len(item_cat)
        print("Dictionary Length")
        print(len(dict_cat))
        print(dict_cat)

        # Check if the user is logged in and is the creator of item
        is_owner = False
        if 'username' in login_session:
            user_logged_in = True
        else:
            user_logged_in = False
        return render_template('items.html',
                               categories=categories, items=items,
                               category_name=category, num=number_of_items,
                               dict_cat=dict_cat,
                               user_logged_in=user_logged_in)
    elif request.method == 'POST':
        return "Inside the post items for the category: %s" % category


# Route for getting the description of the item
@app.route('/catalog/<category>/<item>', methods=['GET', 'POST'])
def getDescription(category, item):
    if request.method == 'GET':
        item = session.query(Items).\
            filter_by(item_cat_name=category, item_name=item).first()
        item_desc = item.item_description
        creator = getuserinfo(item.user_id)

        # Check if the user is logged in and is the creator of item
        is_owner = False
        if 'username' in login_session:
            user_logged_in = True
            if creator.id == login_session['user_id']:
                is_owner = True
        else:
            user_logged_in = False
        return render_template('descriptionItem.html',
                               item=item, user_logged_in=user_logged_in,
                               is_owner=is_owner)


# Route for adding a new item to the category
@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    categories = session.query(Category).all()
    if request.method == 'GET':
        return render_template('addItem.html', categories=categories)
    else:
        item_cat_name = request.form.get('category_select')
        print(item_cat_name)
        item_cat_id = getCatagoryId(item_cat_name)
        print(item_cat_id)
        newitem = Items()
        newitem.item_name = request.form['item_name']
        newitem.item_description = request.form['item_description']
        newitem.cat_item_id = item_cat_id
        newitem.item_cat_name = item_cat_name
        session.add(newitem)
        session.commit()
        return redirect(url_for('getAllCategories'))


# Route for editing the item
@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def editItem(item):
    item_for_edit = session.query(Items).filter_by(item_name=item).first()
    print(item_for_edit)
    if request.method == 'GET':
        categories = session.query(Category).all()
        creator = getuserinfo(item_for_edit.user_id)

        # Check if the user is logged in and is the creator of item
        is_owner = False
        if 'username' in login_session:
            user_logged_in = True
            if creator.id == login_session['user_id']:
                is_owner = True
        else:
            user_logged_in = False
        return \
            render_template('editItem.html',
                            item=item_for_edit, categories=categories,
                            is_owner=is_owner, user_logged_in=user_logged_in)
    elif request.method == 'POST':
        print("Inside post")
        print(request.form['item_name'])
        item_for_edit.item_name = request.form['item_name']
        item_for_edit.item_description = request.form['item_description']
        item_for_edit.item_cat_name = request.form.get('category_select')
        session.add(item_for_edit)
        session.commit()
        return redirect(url_for('getAllCategories'))


# Route for deleting the item
@app.route('/catalog/<item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
    item_to_delete = session.query(Items).filter_by(item_name=item).one()
    print(item_to_delete.item_name)
    if request.method == 'GET':
        creator = getuserinfo(item_to_delete.user_id)

        # Check if the user is logged in and is the creator of item
        is_owner = False
        if 'username' in login_session:
            user_logged_in = True
            if creator.id == login_session['user_id']:
                is_owner = True
        else:
            user_logged_in = False
        return render_template('deleteItem.html', item=item_to_delete,
                               is_owner=is_owner,
                               user_logged_in=user_logged_in)
    elif request.method == 'POST':
        print(item_to_delete.item_name)
        session.delete(item_to_delete)
        session.commit()
        return redirect(url_for('getAllCategories'))
        # return "Inside Post"


# Route for accessing my applications data that is exposed
@app.route('/catalog.json')
def getJSONData():
    items = session.query(Items).all()
    return jsonify(items=[item.Serialize for item in items])


# Method to get the Category id for the category name
def getCatagoryId(catagory_name):
    category_column = session.query(Category).\
        filter_by(cat_name=catagory_name).first()
    category_id = category_column.cat_id
    return category_id


# Get the category name using the item name
def getCategoryName(item_name):
    item_row = session.query(Items).filter_by(item_name=item_name).first()
    item_cat_id = item_row.cat_item_id
    category_name = session.query(Category).filter_by(cat_id=item_cat_id).one()
    return category_name


# Main method listen to the incoming requests at port 8000
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
