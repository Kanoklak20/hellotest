import json
from flask import (jsonify, render_template,
                  request, url_for, flash, redirect, session)
from sqlalchemy.sql import text
from app import app
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.urls import url_parse
from sqlalchemy.sql import text
from flask_login import login_user,login_required,logout_user
from app import login_manager
from app.models.authuser import UserInfo
from app.models.authuser import Reservations
from app.models.authuser import Tables
from flask_login import login_user, login_required, logout_user, current_user
import secrets
import string
from app import oauth
import os
#import forms
from dotenv import load_dotenv
load_dotenv('.env.dev')
from sqlalchemy import and_

@app.route('/')
def home():
    return render_template('home.html')

def read_file(filename, mode="rt"):
    with open(filename, mode, encoding='utf-8') as fin:
        return fin.read()
    
def write_file(filename, contents, mode="wt"):
    with open(filename, mode, encoding="utf-8") as fout:
        fout.write(contents)

@app.route('/ticket')
@login_required
def ticket():
    reservation_id = session.get('reservation')
    reservation = Reservations.query.filter_by(id=reservation_id).first()
    if reservation:
        content = {
            'id': reservation.id,
            'date': reservation.date,
            'table_id': reservation.table.no,
            'owner_id': reservation.owner_id,
            'firstname': current_user.firstname,
            'lastname': current_user.lastname
        }
        return render_template('ticket.html',contents=[content])




@app.route('/db')
def db_connection():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return '<h1>db works.</h1>'
    except Exception as e:
        return '<h1>db is broken.</h1>' + str(e)

@login_manager.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # login code goes here
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        user = UserInfo.query.filter_by(email=email).first()
 
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the
        # hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            # if the user doesn't exist or password is wrong, reload the page
            return redirect(url_for('login'))
        
        
        # if the above check passes, then we know the user has the right
        # credentials
        login_user(user, remember=remember)
        if user.role == 'admin':
            return redirect(url_for('booked'))
        next_page = request.args.get('next')
        if (not next_page or url_parse(next_page).netloc != '') and user.role == 'customer':
            next_page = url_for('booking')
        return redirect(next_page)
        
    return render_template('login.html')

@app.route('/google/')
def google():

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app   .config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


   # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    app.logger.debug(str(token))
    userinfo = token['userinfo']
    app.logger.debug(" Google User " + str(userinfo))
    email = userinfo['email']
    firstname= userinfo['given_name']
    lastname= userinfo['family_name']
    phone_no=""
    birth='10-10-2000'
    
    user = UserInfo.query.filter_by(email=email).first()


    if not user:
        username = userinfo.get('given_name','') + " " + userinfo.get('family_name','')
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        new_user = UserInfo(email=email,firstname=firstname, lastname=lastname,
                        phone_no=phone_no,birth=birth,
                           password=generate_password_hash(
                               password, method='sha256'),username=username,role="customer")
        db.session.add(new_user)
        db.session.commit()
        user = UserInfo.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/booking')

@app.route('/github/')
def github():
    # Github Oauth Config

    # GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_ID = app.config['GITHUB_CLIENT_ID']
    # GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    GITHUB_CLIENT_SECRET = app.config['GITHUB_CLIENT_SECRET']

    print("--- Client ID: ", GITHUB_CLIENT_ID)
    print("--- Client Secret: ", GITHUB_CLIENT_SECRET)
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        consumer_secret=GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'email'},
    )
    redirect_uri = url_for('github_auth', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)
 
@app.route('/github/auth/')
def github_auth():
    token = oauth.github.authorize_access_token()
    app.logger.debug(str(token))
    userinfo = token['userinfo']
    app.logger.debug(" GITHUB User " + str(userinfo))
    email = userinfo['email']
    name= userinfo['name']
    print("Github User" + str(userinfo))
    app.logger.debug("GitHub User" + str(userinfo))
    
    user = UserInfo.query.filter_by(email=email).first()


    if not user:
        # username = userinfo.get('given_name','') + " " + userinfo.get('family_name','')
        random_pass_len = 8
        password = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                          for i in range(random_pass_len))
        new_user = UserInfo(email=email,name=name,
                           password=generate_password_hash(
                               password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        user = UserInfo.query.filter_by(email=email).first()
    login_user(user)
    return redirect('/booking')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        result = request.form.to_dict()
        app.logger.debug(str(result))
 
        validated = True
        validated_dict = {}
        valid_keys = ['name', 'surname', 'email', 'user', 'phone', 'date', 'password', 'cfpassword']

        # validate the input
        for key in result:
            app.logger.debug(str(key)+": " + str(result[key]))
            # screen of unrelated inputs
            if key not in valid_keys:
                continue

            value = result[key].strip()
            if not value or value == 'undefined':
                validated = False
                break
            validated_dict[key] = value
            # code to validate and add user to database goes here
        app.logger.debug("validation done")
        if validated:
            app.logger.debug('validated dict: ' + str(validated_dict))
            name = validated_dict['name']
            surname = validated_dict['surname']
            email = validated_dict['email']
            user = validated_dict['user']
            phone = validated_dict['phone']
            date = validated_dict['date']
            password = validated_dict['password']
            cfpassword = validated_dict['cfpassword']
            # if this returns a user, then the email already exists in database
            user = UserInfo.query.filter_by(email=email).first()

            if password != cfpassword:
                flash('Password not match')
                return redirect(url_for('signup'))

            if user:
                # if a user is found, we want to redirect back to signup
                # page so user can try again
                flash('Email address already exists')
                return redirect(url_for('signup'))

            # create a new user with the form data. Hash the password so
            # the plaintext version isn't saved.
            app.logger.debug("preparing to add")
            new_user = UserInfo(firstname=name, lastname=surname, email=email, phone_no=phone, birth=date,
                                password=generate_password_hash(password, method='sha256'), username=user,role='customer')
            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/booking',methods=('GET','POST'))
@login_required
def booking():
    if request.method == 'POST':
        email=current_user.email
        firstname=current_user.firstname
        lastname=current_user.lastname
        phone=current_user.phone_no
        date = request.form['date']
        table = request.form.get('tickets')
        if not date:
            flash('Date is required!')
        elif not ticket :
            flash('Ticket is required!')
        else:
            exist = Reservations.query.filter_by(date = date).first()
            # print(exist)
            if exist and exist.table.no == table:
                flash('This reservation already exists!')
            else:
                seat = Tables(no=table,date=date,status=False)
                db.session.add(seat)
                db.session.commit()
                entry = Reservations(date=date,table_id=seat.id,owner_id=current_user.id)
                app.logger.debug(str(entry))
                db.session.add(entry)
                db.session.commit()
                session['reservation'] = entry.id
                return redirect(url_for('ticket'))

    return render_template('booking.html')


@app.route('/booked')
@login_required
def booked():
    return render_template('bookedtable.html')

@app.route("/booked-f1d")
@login_required
def booked_stored_contacts():
    raw_json = read_file('app/data/stored_contacts.json')
    contacts = json.loads(raw_json)

    return jsonify(contacts)


@app.route("/user")
def user_settings():
    return render_template('user.html')

@app.route("/data")
def data():
    contacts = []
    db_contacts = Reservations.query.all()
    contacts = list(map(lambda x: x.to_dict(), db_contacts))
    app.logger.debug("DB Contacts: " + str(contacts))
    return jsonify(contacts)

@app.route('/booked/remove_contact', methods=('GET', 'POST'))
def lab10_remove_contacts():
    app.logger.debug("BOOKED - REMOVE")
    if request.method == 'POST':
        result = request.form.to_dict()
        id_ = result.get('id', '')
        try:
            contact = Reservations.query.get(id_)
            db.session.delete(contact)
            db.session.commit()
        except Exception as ex:
           app.logger.error(f"Error removing contact with id {id_}: {ex}")
           raise
    return data()