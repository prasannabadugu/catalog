from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, EclgName, StateName, User
from flask import session as usr_login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///eng_clgs.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Engineering colleges"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
cgs_cat = session.query(StateName).all()


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    usr_login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    cgs_cat = session.query(StateName).all()
    cges = session.query(EclgName).all()
    return render_template('login.html',
                           STATE=state, cgs_cat=cgs_cat, cges=cges)
    # return render_template('myhome.html', STATE=state
    # cgs_cat=cgs_cat,cges=cges)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != usr_login_session['state']:
        gml_res = make_response(json.dumps('Invalid state parameter.'), 401)
        gml_res.headers['Content-Type'] = 'application/json'
        return gml_res
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        trgm_oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='')
        trgm_oauth_flow.redirect_uri = 'postmessage'
        credentials = trgm_oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        gml_res = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        gml_res.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        gml_res = make_response(json.dumps(result.get('error')), 500)
        gml_res.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        gml_res = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        gml_res.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        gml_res = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = usr_login_session.get('access_token')
    stored_gplus_id = usr_login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        gml_res = make_response(json.dumps(
            'Current user already connected.'), 200)
        gml_res.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    usr_login_session['access_token'] = credentials.access_token
    usr_login_session['gplus_id'] = gplus_id

    # Get user info
    gm_usrinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    gm_params = {'access_token': credentials.access_token, 'alt': 'json'}
    gm_ans = requests.get(gm_usrinfo_url, params=gm_params)

    lgusr_data = gm_ans.json()

    usr_login_session['username'] = lgusr_data['name']
    usr_login_session['picture'] = lgusr_data['picture']
    usr_login_session['email'] = lgusr_data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(usr_login_session['email'])
    if not user_id:
        user_id = createUser(usr_login_session)
    usr_login_session['user_id'] = user_id
    clg_opt = ''
    clg_opt += '<h1>Welcome,'
    clg_opt += usr_login_session['username']
    clg_opt += '!</h1>'
    clg_opt += '<img src="'
    clg_opt += usr_login_session['picture']
    clg_opt += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % usr_login_session['username'])
    print ("done!")
    return clg_opt


# User Helper Functions
def createUser(usr_login_session):
    User_lgin1 = User(
        name=usr_login_session['username'],
        email=usr_login_session['email'],
        picture=usr_login_session['picture'])
    session.add(User_lgin1)
    session.commit()
    user = session.query(User).filter_by(
        email=usr_login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

# Home


@app.route('/')
@app.route('/home')
def home():
    cgs_cat = session.query(StateName).all()
    return render_template('myhome.html', cgs_cat=cgs_cat)

#####
# college Category for admins


@app.route('/colleges')
def colleges():
    try:
        if usr_login_session['username']:
            name = usr_login_session['username']
            cgs_cat = session.query(StateName).all()
            cgs = session.query(StateName).all()
            cges = session.query(EclgName).all()
            return render_template('myhome.html', cgs_cat=cgs_cat,
                                   cgs=cgs, cges=cges, uname=name)
    except:
        return redirect(url_for('showLogin'))

######


# Showing colleges based on college category


@app.route('/colleges/<int:cgid>/AllColleges')
def showStates(cgid):
    cgs_cat = session.query(StateName).all()
    cgs = session.query(StateName).filter_by(id=cgid).one()
    cges = session.query(EclgName).filter_by(statenameid=cgid).all()
    try:
        if usr_login_session['username']:
            return render_template('showColleges.html', cgs_cat=cgs_cat,
                                   cgs=cgs, cges=cges,
                                   uname=usr_login_session['username'])
    except:
        return render_template('showColleges.html',
                               cgs_cat=cgs_cat, cgs=cgs, cges=cges)

#####
# Add New state


@app.route('/colleges/addStateName', methods=['POST', 'GET'])
def addStateName():
    if request.method == 'POST':

                # check if user is logged in or not

        if 'email' in usr_login_session and \
                    usr_login_session['email'] != 'null':

            company = StateName(st_name=request.form['name'],
                                user_id=usr_login_session['user_id'])
            session.add(company)
            session.commit()
            return redirect(url_for('colleges'))
        else:
            return render_template('login')
    else:
        return render_template('addStateName.html', cgs_cat=cgs_cat)

########
# Edit college Category


@app.route('/colleges/<int:cgid>/edit', methods=['POST', 'GET'])
def editCollegeCategory(cgid):
    editedCollege = session.query(StateName).filter_by(id=cgid).one()
    creator = getUserInfo(editedCollege.user_id)
    user = getUserInfo(usr_login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != usr_login_session['user_id']:
        flash("You cannot edit this state Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('colleges'))
    if request.method == "POST":
        if request.form['name']:
            editedCollege.st_name = request.form['name']
        session.add(editedCollege)
        session.commit()
        flash("State Category Edited Successfully")
        return redirect(url_for('colleges'))
    else:
        # cgs_cat is global variable we can them in entire application
        return render_template('editCollegeCategory.html',
                               cg=editedCollege, cgs_cat=cgs_cat)

######


# Delete college Category
@app.route('/colleges/<int:cgid>/delete', methods=['POST', 'GET'])
def deleteCollegeCategory(cgid):
    cg = session.query(StateName).filter_by(id=cgid).one()
    creator = getUserInfo(cg.user_id)
    user = getUserInfo(usr_login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != usr_login_session['user_id']:
        flash("You cannot Delete this college Category."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('colleges'))
    if request.method == "POST":
        session.delete(cg)
        session.commit()
        flash("college Category Deleted Successfully")
        return redirect(url_for('colleges'))
    else:
        return render_template('deleteCollegeCategory.html',
                               cg=cg, cgs_cat=cgs_cat)

######
# Add New College Details


@app.route('/colleges/addStateName/addCollegeDetails/<string:cgname>/add',
           methods=['GET', 'POST'])
def addCollegeDetails(cgname):
    cgs = session.query(StateName).filter_by(st_name=cgname).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(cgs.user_id)
    user = getUserInfo(usr_login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != usr_login_session['user_id']:
        flash("You can't add new book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showStates', cgid=cgs.id))
    if request.method == 'POST':
        name = request. form['name']
        branch = request. form['branches']
        year = request. form['year']
        phone = request. form['ph']
        email = request. form['email']
        website = request. form['website']
        collegedetails = EclgName(clg_name=name, branches=branch,
                                  esta_year=year,
                                  clg_phn=phone, clg_email=email,
                                  web_site=website,
                                  statenameid=cgs.id,
                                  user_id=usr_login_session['user_id'])
        session.add(collegedetails)
        session.commit()
        return redirect(url_for('showStates', cgid=cgs.id))
    else:
        return render_template('addCollegeDetails.html',
                               cgname=cgs.st_name, cgs_cat=cgs_cat)

######
# Edit college details


@app.route('/colleges/<int:cgid>/<string:cgename>/edit',
           methods=['GET', 'POST'])
def editCollege(cgid, cgename):
    cg = session.query(StateName).filter_by(id=cgid).one()
    collegedetails = session.query(EclgName).filter_by(clg_name=cgename).one()
    # See if the logged in user is not the owner of college
    creator = getUserInfo(cg.user_id)
    user = getUserInfo(usr_login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != usr_login_session['user_id']:
        flash("You can't edit this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('colleges', cgid=cg.id))
    # POST methods
    if request.method == 'POST':
        collegedetails.clg_name = request.form['name']
        collegedetails.branches = request.form['branches']
        collegedetails.esta_year = request.form['year']
        collegedetails.clg_phn = request.form['phn']
        collegedetails.clg_email = request.form['email']
        collegedetails.web_site = request.form['website']
        session.add(collegedetails)
        session.commit()
        flash("college Edited Successfully")
        return redirect(url_for('showStates', cgid=cgid))
    else:
        return render_template('editCollege.html',
                               cgid=cgid, collegedetails=collegedetails,
                               cgs_cat=cgs_cat)

#####
# Delte college Edit


@app.route('/colleges/<int:cgid>/<string:cgename>/delete',
           methods=['GET', 'POST'])
def deleteCollege(cgid, cgename):
    cg = session.query(StateName).filter_by(id=cgid).one()
    collegedetails = session.query(EclgName).filter_by(clg_name=cgename).one()
    # See if the logged in user is not the owner of byke
    creator = getUserInfo(cg.user_id)
    user = getUserInfo(usr_login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != usr_login_session['user_id']:
        flash("You can't delete this book edition"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('colleges', cgid=cg.id))
    if request.method == "POST":
        session.delete(collegedetails)
        session.commit()
        flash("Deleted college Successfully")
        return redirect(url_for('colleges', cgid=cgid))
    else:
        return render_template('deleteCollege.html',
                               cgid=cgid, collegedetails=collegedetails,
                               cgs_cat=cgs_cat)

####
# Logout from current user


@app.route('/logout')
def logout():
    access_token = usr_login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (usr_login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        lgt_res = make_response(
            json.dumps('Current user not connected....'), 401)
        lgt_res.headers['Content-Type'] = 'application/json'
        return response
    access_token = usr_login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'}
                  )[0]

    print (result['status'])
    if result['status'] == '200':
        del usr_login_session['access_token']
        del usr_login_session['gplus_id']
        del usr_login_session['username']
        del usr_login_session['email']
        del usr_login_session['picture']
        lgt_res = make_response(
            json.dumps('Successfully disconnected user..'), 200)
        lgt_res.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        lgt_res = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        lgt_res.headers['Content-Type'] = 'application/json'
        return response
# Json


@app.route('/colleges/JSON')
def allCollegesJSON():
    collegecategories = session.query(StateName).all()
    category_dict = [c.serialize for c in collegecategories]
    for c in range(len(category_dict)):
        colleges = [i.serialize for i in session.query(
                 EclgName).filter_by(statenameid=category_dict[c]["id"]).all()]
        if colleges:
            category_dict[c]["college"] = colleges
    return jsonify(StateName=category_dict)

####


@app.route('/colleges/collegeCategories/JSON')
def categoriesJSON():
    colleges = session.query(StateName).all()
    return jsonify(collegeCategories=[c.serialize for c in colleges])

####


@app.route('/colleges/college/JSON')
def itemsJSON():
    items = session.query(EclgName).all()
    return jsonify(colleges=[i.serialize for i in items])

#####


@app.route('/colleges/<path:college_name>/college/JSON')
def categoryItemsJSON(college_name):
    collegeCategory = session.query(StateName).filter_by(
        st_name=college_name).one()
    colleges = session.query(EclgName).filter_by(
        statename=collegeCategory).all()
    return jsonify(collegeEdtion=[i.serialize for i in colleges])

#####


@app.route('/colleges/<path:college_name>/<path:edition_name>/JSON')
def ItemJSON(college_name, edition_name):
    collegeCategory = session.query(StateName).filter_by(
        st_name=college_name).one()
    collegeEdition = session.query(EclgName).filter_by(
        clg_name=edition_name, statename=collegeCategory).one()
    return jsonify(collegeEdition=[collegeEdition.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=9876)
