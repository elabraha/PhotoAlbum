# --- app.py --- #

from flask import Flask, render_template, flash, request, session, redirect, url_for
from flask.ext.mysqldb import MySQLdb
import time, os, datetime, re, json
from passlib.hash import bsdi_crypt
from flask import jsonify
#from api import *
import ast
import requests

#import requests

app = Flask(__name__)
db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit",\
cursorclass=MySQLdb.cursors.DictCursor)
# db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + '/static/pictures/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'gif', 'bmp'])

app.secret_key = '\xff<6\xad\xbb\x98\x18\xdb\x1a\xe4\xb5\x8b\xa0#7\x10\xf8J\x04\xb3s\t\xf3\x85'

app.permanent_session_lifetime = datetime.timedelta(minutes=5)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def sql_query(sql, c):
    c.execute(sql)
    return c.fetchall()

def get_pub_albums(c):
    sql = "SELECT username FROM Album WHERE access = 'public' GROUP BY username"
    pub_users = sql_query(sql, c)

    publ_dict = dict()
    for item in pub_users:
        publ_dict[item['username']]= []

    sql = "SELECT u.username, a.albumid, a.title FROM User u, Album a WHERE a.access = 'public' AND a.username = u.username"
    pub_albums = sql_query(sql, c)
    
    for alb in pub_albums:
        publ_dict[alb['username']].append((alb['albumid'], alb['title']))
    return publ_dict;

def last_updated(c, db, albumid):
    sql_change_album_time = "UPDATE Album SET lastupdated = NOW() WHERE albumid\
                    ='%s'" % albumid
    c.execute(sql_change_album_time)
    db.commit()

def is_valid_username(username):
    if not re.match("[A-Za-z0-9_]{3,20}", username):
        return False
    return True

def is_valid_name(name):
    return len(name) <= 20

def is_valid_email(email):
    if not re.match("[a-zA-Z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,3}$", email):
        return False
    return True

def is_valid_password(password):
    if not re.match("^(?=.*\d)(?=.*[a-zA-Z]).{5,15}$", password):
        return False
    return True

def execute(query, db):
    c = db.cursor()
    c.execute(query)
    return c.fetchall()

def update(query, db):
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    return cursor.lastrowid

def get_pic_by_id(picid):
    query = "SELECT picid, url, format, date FROM Photo WHERE picid='%s'" % (picid)
    results = execute(query)
    if len(results) > 0:
        pic = Pic(*results[0])
        return pic
    else:
        raise RecordNotFound(resource_type='Pic', source={"pointer": "data/attributes/picid"})

###############################################################################

# modify session before every request:
@app.before_request
def func():
  session.modified = True

# Homepage
@app.route('/ofvujvy4x6r/pa4', methods=['GET', 'POST'])
def index():

    db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
    cursorclass=MySQLdb.cursors.DictCursor)
    # db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()

    if request.method == 'POST':
        if request.form.get('op') == "signup":
            hash = bsdi_crypt.encrypt(request.form.get('password'))
            sql_check = "SELECT username FROM User WHERE username='%s'" % request.form.get('username')
            c.execute(sql_check)
            username_exists = c.fetchall()
            error = False;
            if len(username_exists) != 0:
                error_message = 'Username %s already exists. Please pick another username' % username_exists[0]['username']
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            new_username = request.form.get('username')
            if not is_valid_username(new_username):
                error_message='Invalid Username: username must contain only letters, numbers, or underscores and cannot exceed 20 characters.'
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            new_firstname = request.form.get('firstname')
            if not is_valid_name(new_firstname):
                error_message='Invalid Name: First and last name cannot exceed 20 characters.'
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            new_lastname = request.form.get('lastname')
            if not is_valid_name(new_lastname):
                error_message='Invalid Name: First and last name cannot exceed 20 characters.'
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            new_password = str(request.form.get('password'))
            if not is_valid_password(new_password):
                error_message='Invalid Password: Password must be between 5 and 15 characters, contain only letters numbers and underscores, and contain at least one letter and one number.'
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            new_password2 = str(request.form.get('password2'))
            if not is_valid_password(new_password2):
                error_message='Invalid Password: Password must be between 5 and 15 characters, contain only letters numbers and underscores, and contain at least one letter and one number.'
                flash(error_message)
                error = True            
            if new_password2 != new_password:
                error_message='Invalid Password: Passwords do not match.' 
                flash(error_message)
                error = True                 
            new_email = request.form.get('email')
            if not is_valid_email(new_email):
                error_message='Invalid Email: Email must be of the form something@something.com (after . you must only have 2 or 3 characters).'
                flash(error_message)
                error = True
                # return redirect(url_for('user'))
            if (error):
                return redirect(url_for('user'))
            sql = "INSERT INTO User(username, firstname, lastname, password, email) \
            VALUES ('%s', '%s', '%s', '%s', '%s')" % (request.form.get('username'), \
            request.form.get('firstname'), request.form.get('lastname'), \
            str(hash), request.form.get('email'))
            c.execute(sql)
            db.commit()
        elif request.form.get('op') == "delete":
            sql = "DELETE FROM User WHERE username='%s'" %session['username']
            c.execute(sql)
            db.commit()
            session.pop('username', None)

    if 'username' in session:
        sql = "SELECT m.albumid, a.username, a.title from AlbumAccess m, Album a \
        WHERE m.username = '%s' AND a.albumid = m.albumid" %session['username']
        album_accessible = sql_query(sql, c)
        publ_dict = get_pub_albums(c)

        # --- combine private accesible albums and public albums into one dictionary --- #
        for item in album_accessible:
            if item['username'] in publ_dict.keys():
                publ_dict[item['username']].append((item['albumid'], item['title']))
            else:
                publ_dict[item['username']] = []
                publ_dict[item['username']].append((item['albumid'], item['title']))

        return render_template("index.html", login=session['username'], album=publ_dict)

    c.close()
    db.close()
    return render_template("index.html")

###############################################################################

# Login Page
@app.route('/ofvujvy4x6r/pa4/user/login', methods=['GET', 'POST'])
def login():
    # db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()

    url = request.args.get('url')

    if request.method == 'POST':
        username = request.form.get('username')
        data_user = "SELECT username FROM User WHERE username = '%s'" %username
        validate_user = sql_query(data_user, c)
        if len(validate_user) == 0:
            return render_template('login.html', user_error=username)

        password = request.form.get('password')
        data_pass = "SELECT password FROM User WHERE username = '%s'" %username
        validate_pass = sql_query(data_pass, c)
        if bsdi_crypt.verify(password, validate_pass[0]['password']):
            session['username'] = request.form['username']
            if url is not None:
                return redirect(url)
            else:
                return redirect(url_for('index'))
            
        else:
            return render_template('login.html', pass_error=username)
        session.permanent = True

    c.close()
    db.close()
    return render_template("login.html")

###############################################################################

# --- Signup --- #
@app.route('/ofvujvy4x6r/pa4/user', methods=['GET', 'POST'])
def user():
    if 'username' in session:
        return redirect(url_for('user_edit'))
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()

    c.close()
    db.close()
    return render_template("user.html")

###############################################################################

# --- Edit User --- #
@app.route('/ofvujvy4x6r/pa4/user/edit', methods=['GET', 'POST'])
def user_edit():

    if 'username' in session:
        # db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
        # cursorclass=MySQLdb.cursors.DictCursor)
        db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
        c = db.cursor()
        sql = "SELECT * FROM User WHERE username='%s'" %session['username']
        user_info = sql_query(sql, c)
         

        if request.method == "POST":
            if request.form.get('op') == 'changefirst':
                new_firstname = request.form.get('firstname')
                if not is_valid_name(new_firstname):
                    error_message='Invalid Name: First and last name cannot exceed 20 characters.'
                    flash(error_message)
                    error = True
                    return redirect(url_for('user_edit'))
                sql = "UPDATE User SET firstname='%s' WHERE username='%s'" %(request.form.get('firstname'), session['username'])
                c.execute(sql)
                db.commit() 
            elif request.form.get('op') == 'changelast':
                new_lastname = request.form.get('lastname')
                if not is_valid_name(new_lastname):
                    error_message='Invalid Name: First and last name cannot exceed 20 characters.'
                    flash(error_message)
                    error = True
                    return redirect(url_for('user_edit'))
                sql = "UPDATE User SET lastname='%s' WHERE username='%s'" %(request.form.get('lastname'), session['username'])
                c.execute(sql)
                db.commit()
            elif request.form.get('op') == 'changeemail':
                new_email = request.form.get('email')
                if not is_valid_email(new_email):
                    error_message='Invalid Email: Email must be of the form something@something.com (after . you must only have 2 or 3 characters).'
                    flash(error_message)
                    error = True
                    return redirect(url_for('user_edit'))
                sql = "UPDATE User SET email='%s' WHERE username='%s'" %(request.form.get('email'), session['username'])
                c.execute(sql)
                db.commit()
            elif request.form.get('op') == 'changepass':
                new_password = str(request.form.get('pass'))
                if not is_valid_password(new_password):
                    error_message='Invalid Password: Password must be between 5 and 15 characters, contain only letters numbers and underscores, and contain at least one letter and one number.'
                    flash(error_message)
                    error = True
                    return redirect(url_for('user_edit'))

                if request.form.get('password') == request.form.get('conpassword'):
                    #hashing password
                    new_password2 = str(request.form.get('confirm'))
                    if not is_valid_password(new_password2):
                        error_message='Invalid Password: Password must be between 5 and 15 characters, contain only letters numbers and underscores, and contain at least one letter and one number.'
                        flash(error_message)
                        error = True 
                        return redirect(url_for('user_edit'))           
                    if new_password2 != new_password:
                        error_message='Invalid Password: Passwords do not match.' 
                        flash(error_message)
                        error = True 
                        return redirect(url_for('user_edit'))
                    hash = bsdi_crypt.encrypt(request.form.get('password'))
                    sql = "UPDATE User SET password='%s' WHERE username='%s'" %\
                    (str(hash), session['username'])
                    c.execute(sql)
                    db.commit()
                else:
                    return render_template("user_edit.html", login=session['username'], user_info=user_info, pass_no_match=True)


        c.close()
        db.close()

        
        return render_template("user_edit.html", login=session['username'], user_info=user_info)
    else:
        return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %url_for('user_edit'))

###############################################################################

# --- Logout --- #
@app.route('/ofvujvy4x6r/pa4/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

###############################################################################

# --- Albums --- #

@app.route('/ofvujvy4x6r/pa4/albums', methods=['GET', 'POST'])
def albums():
    # who can access: public, private but given access
    # db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()
    if 'username' in session:

        user = session["username"]

        # --- Check for valid user --- #
        user_sql = "SELECT username FROM User WHERE username = '%s'" % user
        username = sql_query(user_sql, c)
        if user is None or len(username) == 0:
            abort(404)

    # ----------------------------------------------------------------------- #

        # --- Check for add or delete input --- #
        if request.method == 'POST':

            # --- Add album --- #
            if request.form.get('op') == 'add':
                sql_add = "INSERT INTO Album(title, created, lastupdated, username, access)\
                    VALUES('%s', NOW(), NOW(), '%s', '%s')" % \
                    (request.form.get('title'), user, request.form.get('access'))
                c.execute(sql_add)
                db.commit()

            # --- Delete album --- #
            if request.form.get('op') == 'delete':
                albumid = request.form['albumid']
                photo_delete_sql = "SELECT url FROM Photo WHERE albumid = %s" % albumid
                photos_to_delete = sql_query(photo_delete_sql, c)
                for photo in photos_to_delete:
                    path = "./static" + photo['url']
                    os.remove(path)
                sql = "DELETE FROM Album where albumid = %s" % albumid
                c.execute(sql)
                db.commit()


        sql = "SELECT albumid, title FROM Album WHERE username = '%s'" %session['username']
        albums = sql_query(sql, c)

        c.close()
        db.close()

        return render_template("albums.html", login=session['username'], albums=albums)

    else:
        publ_dict = get_pub_albums(c)

        c.close()
        db.close()

        return render_template("albums.html", public=publ_dict)

###############################################################################

# --- Edit Albums --- #
@app.route('/ofvujvy4x6r/pa4/albums/edit')
def albums_edit():

    if 'username' in session:
        #update who can view
        # db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
        #     cursorclass=MySQLdb.cursors.DictCursor)
    
        db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

        # --- Recieve user --- #
        user = session['username']
        c = db.cursor()

        # --- Check for valid user --- #
        user_sql = "SELECT username FROM User WHERE username = '%s'" % user
        c = db.cursor()
        username = sql_query(user_sql, c)
        if user is None or len(username) == 0:
            abort(404)

        # ----------------------------------------------------------------------- #

        # --- Render HTML --- #
        sql = "SELECT title, albumid, access FROM Album WHERE username='%s'" % user
        albums = sql_query(sql, c)
        c.close()
        db.close()

        
        return render_template("albums_edit.html", albums=albums, edit="True", \
            login=session['username'])
    else:
        return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %url_for('albums_edit'))

###############################################################################

# --- Album --- #
@app.route('/ofvujvy4x6r/pa4/album', methods=['GET', 'POST'])
def album():
    # db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

    # --- Recieve Form --- #
    albumid = request.args.get('id')
    c = db.cursor()

    # --- Check for valid album --- #
    id_sql = "SELECT albumid FROM Album WHERE albumid = '%s'" % albumid
    id = sql_query(id_sql, c)
    if id is None or len(id) == 0:
        abort(404)

    sql = "SELECT access FROM Album WHERE albumid = %s" %albumid
    access_type = sql_query(sql, c)[0]['access']

    # ----------------------------------------------------------------------- #

    # --- Check for add or delete input --- #
    if request.method == 'POST':

        # --- Add photo -- #
        if request.form.get('op') == 'add':

            file = request.files['photo']
            if not allowed_file(file.filename):

                pass #what do we do about this??
                #what if the file doesn't exist or is in the wrong format

            else:
                filename = file.filename

                # --- Hash picid --- #
                hashing = str(hash(filename + str(time.time())))
                if hashing[0] == '-':
                    hashing = 'x' + hashing

                # --- Update databae --- #
                format_ = filename.rsplit('.', 1)[1]
                url = "/pictures/" + hashing + "." + format_
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                sql_add = "INSERT INTO Photo(picid, albumid, url, format, date)\
                    VALUES('%s', %s, '%s', '%s', '%s')" % (hashing,
                     albumid, url, format_, timestamp)
                sql_change_album_time = "UPDATE Album SET lastupdated = '%s' WHERE albumid\
                    ='%s'" % (timestamp, albumid)
                c.execute(sql_change_album_time)
                db.commit()
                sql_contain = "SELECT MAX(sequencenum) FROM Contain WHERE\
                 albumid = %s" % albumid
                max_dict = sql_query(sql_contain, c)
                sql = "SELECT albumid FROM Contain WHERE albumid = %s" % albumid
                check_seqnum = sql_query(sql, c)
                if (len(check_seqnum) == 0):
                    new_sqnum = 0
                else:
                    new_sqnum = max_dict[0]['MAX(sequencenum)'] + 1

                #do we need the caption??
                sql_insert_cont = "INSERT INTO Contain(albumid, picid, sequencenum)\
                 VALUES(%s, '%s', %s)" % (albumid, hashing, new_sqnum)

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], hashing + '.' + format_))

                c.execute(sql_add)
                c.execute(sql_insert_cont)
                db.commit()

        # --- Delete photo --- #
        if request.form.get('op') == 'delete':

            # --- Update databae --- #
            picid = request.form['picid']
            photo_delete_sql = "SELECT url FROM Photo WHERE picid = '%s'" % picid
            to_delete = sql_query(photo_delete_sql, c)
            url = to_delete[0]['url']
            path = "./static" + url
            os.remove(path)
            sequence_sql = "SELECT sequencenum FROM Contain WHERE picid = '%s' AND albumid = %s"\
             % (picid, albumid)
            sequence_num = sql_query(sequence_sql, c)
            delete = "DELETE FROM Photo WHERE picid = '%s'" % picid
            c.execute(delete)
            update = "UPDATE Contain SET sequencenum = sequencenum - 1 WHERE sequencenum > %s AND albumid = %s" \
            % (sequence_num[0]['sequencenum'], albumid)
            sql_change_album_time = "UPDATE Album SET lastupdated = NOW() WHERE albumid\
                    ='%s'" % albumid
            c.execute(sql_change_album_time)
            c.execute(update)
            db.commit()
        # --- revoke privileges --- #
        if request.form.get('op') == 'revoke':
            user = request.form['user']
            sql = "DELETE FROM AlbumAccess WHERE username = '%s' AND albumid = %s" % (user, albumid)
            c.execute(sql)
            db.commit()
            last_updated(c, db, albumid)
        # --- make public/private access --- #
        if request.form.get('op') == 'update_access':
            access = request.form['access']
            sql = "UPDATE Album SET access = '%s' WHERE albumid = %s" % (access, albumid)
            c.execute(sql)
            db.commit()
            last_updated(c, db, albumid)
        # --- currently having trouble with this --- #
        if request.form.get('op') == 'newuser':
            # return "I got here"
            give_access = request.form['user'];
            check_user_sql = "SELECT username FROM User WHERE username = '%s'" %give_access
            val_user = sql_query(check_user_sql, c)
            sql = "SELECT username FROM AlbumAccess WHERE albumid = %s" %albumid
            has_access = sql_query(sql, c)
            dup_access = False;
            for user in has_access:
                if give_access == user['username']:
                    dup_access = True
            if len(val_user) == 0 or dup_access:
                return redirect('/ofvujvy4x6r/pa3/album/edit?id=%s' %albumid)
            else:
                sql = "INSERT INTO AlbumAccess (username, albumid) VALUES ('%s', %s)" %(give_access, albumid)
                c.execute(sql)
                db.commit()
        if request.form.get('op') == 'make_caption':
            cap = request.form['caption']
            #return 
            cap = cap.replace('"', '\\"').replace("'", "\\'")
            #return cap
            picid = request.form['picid']
            sql = "UPDATE Contain SET caption = '%s' WHERE picid = '%s'" %(cap, picid)
            c.execute(sql)
            db.commit()
            last_updated(c, db, albumid)
        if request.form.get('op') == 'change_album_name':
            album_name = request.form['album_name']
            sql = "UPDATE Album SET title = '%s' WHERE albumid = %s" %(album_name, albumid)
            c.execute(sql)
            db.commit()
            last_updated(c, db, albumid)

    # --- Check if album is empty --- #
    sql_check = "SELECT albumid FROM Contain WHERE albumid=%s" % albumid
    check_empty = sql_query(sql_check, c)
    if len(check_empty) == 0:
        sql = "SELECT title FROM Album WHERE albumid = %s" % albumid
        contains_photos = False
    else:
        contains_photos = True
        sql = "SELECT a.title, p.url, c.picid, c.sequencenum, c.caption, p.date FROM Album a, \
        Photo p, Contain c WHERE a.albumid = %s AND c.albumid = a.albumid AND p.picid \
        = c.picid ORDER BY c.sequencenum ASC" % albumid

    # --- Render HTML --- #
    album_photos = sql_query(sql, c)
    title = album_photos[0]['title']

    # -------------- Deals with if a user can access this album or not ------------------- #
    if contains_photos:
        for item in album_photos:
            #date_obj = datetime.datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
            item['date'] = item['date'].strftime('%m/%d/%Y %I:%M:%S %p')

    # --- gets owner of current album --- #
    sql = "SELECT username FROM Album WHERE albumid = %s" %albumid
    alb_user = sql_query(sql, c)

    if access_type == 'public':
        has_access = True;
    elif 'username' in session and session['username'] == alb_user[0]['username']:
        has_access = True;
    else:
        sql = "SELECT username FROM AlbumAccess WHERE albumid = %s" %albumid
        users_with_access = sql_query(sql, c)
        has_access = False;
        if 'username' in session:
            for user in users_with_access:
                if user['username'] == session['username']:
                    has_access = True;
    # -------------------------------------------------------------------------------------- #



    c.close()
    db.close()
    if 'username' in session:
        if has_access:
            if contains_photos:
                return render_template("pictures.html", login=session['username'], \
                    not_empty=str(contains_photos), album_photos=album_photos, title=title, albumid=albumid, alb_user=alb_user[0]['username'])
            else:
                return render_template("pictures.html", login=session['username'], \
                    album_photos=album_photos, title=title, albumid=albumid, alb_user=alb_user[0]['username'])
        else:
            return redirect(url_for('index')) #what should I do here?
    else: # Check if album is public
        if access_type == 'public':
            if contains_photos:
                return render_template("pictures.html", not_empty=str(contains_photos),\
                 album_photos=album_photos, title=title, albumid=albumid)
            else:
                return render_template("pictures.html", album_photos=album_photos,\
                 title=title, albumid=albumid)
        else:
            string = str(url_for('album')) + '?id=%s' %albumid
            return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %string)

###############################################################################

@app.route('/ofvujvy4x6r/pa4/album/edit', methods=['GET', 'POST'])
def album_edit():
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    c = db.cursor()

    # --- Recieve form --- #
    albumid = request.args.get('id')

    # --- gets owner of current album --- #
    sql = "SELECT username FROM Album WHERE albumid = %s" %albumid
    alb_user = sql_query(sql, c)
    if 'username' in session and session['username'] == alb_user[0]['username']:
        #switch access between public and privates
        #db = MySQLdb.connect(db="group73pa2", user="group73", passwd="iamtheshit", cursorclass=MySQLdb.cursors.DictCursor

        # --- Check for empty album --- #
        sql_check = "SELECT albumid FROM Contain WHERE albumid=%s" % albumid
        check_empty = sql_query(sql_check, c)
        if len(check_empty) == 0:
            sql = "SELECT title FROM Album WHERE albumid = %s" % albumid
            contains_photos = False
        else:
            sql = "SELECT a.title, p.url, c.picid, c.sequencenum FROM Album a, \
                Photo p, Contain c WHERE a.albumid = %s AND c.albumid = %s AND p.picid\
                = c.picid ORDER BY c.sequencenum ASC" % (albumid, albumid)
            contains_photos = True

        sql2 = "SELECT a.albumid, p.username FROM Album a, AlbumAccess p WHERE a.albumid = p.albumid \
        AND p.albumid = '%s'" %albumid
        sql3 = "SELECT access From Album WHERE albumid = %s" % albumid


        # --- Render HTML --- #
        album_photos = sql_query(sql, c)
        title = album_photos[0]['title']

        album_access = sql_query(sql2, c)

        access_type = sql_query(sql3, c)

        if access_type[0]['access'] == 'private':
            acc_type = 'public'
        elif access_type[0]['access'] == 'public':
            acc_type = 'private'

        c.close()
        db.close()
        if (contains_photos):
            return render_template("album_edit.html", login=session['username'], not_empty=str(contains_photos),\
                album_photos=album_photos, title=title, albumid=albumid, access=album_access, access_type=acc_type)
        else:
            return render_template("album_edit.html", login=session['username'], album_photos=album_photos,
                title=title, albumid=albumid, access=album_access, access_type=acc_type)
    else:
        c.close()
        db.close()
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            string = str(url_for('album_edit')) + '?id=%s' %albumid
            return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %string)

###############################################################################

@app.route('/ofvujvy4x6r/pa4/pic', methods=['GET', 'POST'])
def pic():
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

    c = db.cursor()
    # --- Recieve form --- #
    picid = request.args.get('id')

    # --- Check for valid picture --- #
    id_sql = "SELECT picid FROM Photo WHERE picid = '%s'" % picid
    album_sql = "SELECT albumid FROM Photo WHERE picid = '%s'" % picid
    id = sql_query(id_sql, c)
    if id is None or len(id) == 0:
        abort(404)
    albumid_list = sql_query(album_sql, c)
    albumid = albumid_list[0]['albumid']

    # --- gets owner of current album --- #
    sql = "SELECT username FROM Album WHERE albumid = %s" %albumid
    alb_user = sql_query(sql, c)

    # --- Retrieves image url and sequencenum --- #
    sql = "SELECT p.url, c.sequencenum FROM Photo p, Contain c WHERE p.picid = '%s' AND p.picid = c.picid AND \
    c.albumid = '%s' AND p.albumid = '%s'" % (picid, albumid, albumid)
    c = db.cursor()
    thing = sql_query(sql, c)
    url = '/static' + thing[0]['url']
    sequencenum = thing[0]['sequencenum']

    if request.method == 'POST':
        if (request.form.get('op') == 'prev_button' or request.form.get('op') == 'next_button'):
            url = request.form.get('url')
            sequencenum = int(request.form.get('seq'))

    sql = "SELECT max(sequencenum) FROM Contain WHERE albumid = '%s'" % albumid
    maxsequence_list = sql_query(sql, c)
    maxsequence = maxsequence_list[0]['max(sequencenum)']

    if maxsequence > 0:
        if sequencenum == maxsequence:
            next_seq = 0
        else:
            next_seq = sequencenum + 1
        if sequencenum == 0:
            prev_seq = maxsequence
        else:
            prev_seq = sequencenum - 1

        #get prev and next picid
        sql = "SELECT picid FROM Contain WHERE sequencenum = '%s' AND albumid = '%s'" % (prev_seq, albumid)
        c = db.cursor()
        ids = sql_query(sql, c)
        prev_id = ids[0]['picid']
        sql = "SELECT picid FROM Contain WHERE sequencenum = '%s' AND albumid = '%s'" % (next_seq, albumid)
        c = db.cursor()
        ids = sql_query(sql, c)
        next_id = ids[0]['picid']

    if maxsequence > 0:
        sql = "SELECT p.url FROM Photo p, Contain c WHERE c.sequencenum = '%s' AND p.picid = c.picid AND \
        c.albumid = '%s' AND p.albumid = '%s'" % (prev_seq, albumid, albumid)
        c = db.cursor()
        thing = sql_query(sql, c)
        prev_url = '/static' + thing[0]['url']

        sql = "SELECT p.url FROM Photo p, Contain c WHERE c.sequencenum = '%s' AND p.picid = c.picid AND \
        c.albumid = '%s' AND p.albumid = '%s'" % (next_seq, albumid, albumid)
        c = db.cursor()
        thing = sql_query(sql, c)
        next_url = '/static' + thing[0]['url']

    # --- Get caption --- #
    sql = "SELECT caption from Contain where picid = '%s'" %picid
    caption = sql_query(sql, c)
    cap = caption[0]['caption']

    #check if the album is public or private
    sql_check = "SELECT a.access FROM Album a, Photo p WHERE p.picid = '%s' AND a.albumid = p.albumid" % picid
    is_public = sql_query(sql_check, c)

    sql = "SELECT username FROM AlbumAccess WHERE albumid = %s" %albumid
    users_with_access = sql_query(sql, c)

    c.close()
    db.close()

#if not any(d.get('main_color', None) == 'red' for d in a):
 
    if maxsequence > 0:
        if 'username' in session and (session['username'] == alb_user[0]['username'] or\
        any(user.get('username') == session['username'] for user in users_with_access)):
            return render_template("pic.html", url=url, prev_url=prev_url, next_url=next_url, \
                login=session['username'], prev_seq=prev_seq, next_seq=next_seq, prev_id=prev_id,\
                next_id=next_id, caption=cap, picid=picid)
        elif is_public[0]['access'] == 'public':
            if 'username' in session:
                return render_template("pic.html", url=url, prev_url=prev_url, next_url=next_url,\
                    prev_seq=prev_seq, next_seq=next_seq, prev_id=prev_id, next_id=next_id, caption=cap,\
                    login=session['username'], picid=picid)
            else:
                return render_template("pic.html", url=url, prev_url=prev_url, next_url=next_url,\
                    prev_seq=prev_seq, next_seq=next_seq, prev_id=prev_id, next_id=next_id, caption=cap, picid = picid)
        else:
            if 'username' in session:
                return redirect(url_for('index'))
            else:
                string = str(url_for('pic')) + '?id=%s' %picid
                return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %string)
    else:
        if 'username' in session and (session['username'] == alb_user[0]['username'] or\
        any(user.get('username') == session['username'] for user in users_with_access)):
            return render_template("pic.html", url=url, login=session['username'], caption=cap, picid=picid)
        elif is_public[0]['access'] == 'public':
            if 'username' in session:
                return render_template("pic.html", url=url, caption=cap, login=session['username'], picid=picid)
            else:
                return render_template("pic.html", url=url, caption=cap)
        else:
            if 'username' in session:
                return redirect(url_for('index'))
            else:
                string = str(url_for('pic')) + '?id=%s' %picid
                return redirect('/ofvujvy4x6r/pa3/user/login?url=%s' %string)

###############################################################################

@app.route('/ofvujvy4x6r/pa4/pic/caption', methods=['GET'])
def pic_caption_get():
    '''
    Expects URL query parameter with picid.
    Returns JSON with the picture's current caption or error.
    {
        "caption": "current caption"
    }
    {
        "error": "error message",
        "status": 422
    }
    ''' 
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

    picid = request.args.get('id')

    if picid is None:
        r = {"error": "You did not provide an id parameter.", "status": 404}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response

    query = "SELECT caption FROM Contain WHERE picid='%s';" % (picid)
    results = execute(query, db)
    caption = ''
    if len(results) > 0:
        caption = results[0]['caption']
        if caption == None:
            caption = ''
    else:
        r = {"error": "Invalid id parameter. The picid does not exist.", "status": 422 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 422
        db.close()
        return response
    db.close()
    response = jsonify(caption=caption)
    response.status_code = 200
    return response

###############################################################################

@app.route('/ofvujvy4x6r/pa4/pic/caption', methods=['POST'])
def pic_caption_post():
    '''
    Expects JSON POST of the format:
    {
        "caption": "this is the new caption",
        "id": "picid"
    }
    Updates the caption and sends a response of the format
    {
        "caption": "caption",
        "status": 201
    }
    Or if an error occurs:
    {
        "error": "error message",
        "status": 422
    }
    ''' 
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    req_json = request.get_json()

    picid = req_json.get('id')
    caption = req_json.get('caption')

    if caption == None:
        caption = ''

    if picid is None and caption == '':
        r = {"error": "You did not provide an id and caption parameter.", "status": 404 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response
    if picid is None:
        r = {"error": "You did not provide an id parameter.", "status": 404 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response
    if caption == '':
        r = {"error": "You did not provide a caption parameter.", "status": 404 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response

    query = "SELECT picid FROM Contain WHERE picid='%s'" % picid
    result = execute(query, db)
    if len(result) == 0:
        r = {"error": "Invalid id. The picid does not exist.", "status": 422 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 422
        db.close()
        return response

    query = "UPDATE Contain SET caption='%s' WHERE picid='%s';" % (caption, picid)
    update(query, db)

    response = jsonify(caption=caption, status=201)
    response.status_code = 201
    db.close()
    return response

###############################################################################

@app.route('/ofvujvy4x6r/pa4/pic/favorites', methods=['GET'])
def pic_favorite_get():
    '''
    Expects URL query parameter with picid.
    Returns JSON with the picture's id, current number of favorites and latest favorite or error.
    {
        "id": "picid",
        "num_favorites": ###,
        "latest_favorite": "username"
    }
    {
        "error": "error message",
        "status": 422
    }
    ''' 
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)

    picid = request.args.get('id')
    if picid is None:
        r = {"error": "You did not provide an id parameter.", "status": 404 }
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response

    query = "SELECT count(*) FROM Favorite WHERE picid='%s';" % (picid)
    results = execute(query, db)
    query = "SELECT username FROM Favorite WHERE picid='%s' AND date=\
    (SELECT MAX(date) FROM Favorite WHERE picid='%s');" % (picid, picid)
    results2 = execute(query, db)
    if len(results) > 0 and len(results2) > 0:
        num_favorites = results[0]['count(*)']
        latest_favorite = results2[0]['username']
        # num_favorites = str(num_favorites).zfill(2)
    else:
        num_favorites = 0
        latest_favorite = ''
    query = "SELECT * FROM Photo WHERE picid='%s'" %(picid)
    pic = execute(query, db)
    if len(pic) == 0:
        r = {"error": "Invalid id parameter. The picid does not exist.", "status": 422}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 422
        db.close()
        return response
    db.close()
    response = jsonify(id=picid, num_favorites=num_favorites, latest_favorite=latest_favorite)
    response.status_code = 200
    return response

###############################################################################

@app.route('/ofvujvy4x6r/pa4/pic/favorites', methods=['POST'])
def pic_favorite_post():
    '''
    Expects JSON POST of the format:
    {
        "id": "picid",
        "username": "usernameofpersonwhofavorited"
    }
    Updates the number of favorites and latest favorite and sends a response of the format
    {
        "id": "picid",
        "status": 201
    }
    Or if an error occurs:
    {
        "error": "error message",
        "status": 422
    }
    ''' 
    # db = MySQLdb.connect(db="group73pa3", user="group73", passwd="iamtheshit", \
    #     cursorclass=MySQLdb.cursors.DictCursor)
    db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    req_json = request.get_json()

    latest_favorite = req_json.get('username')
    picid = req_json.get('id')

    # latest_favorite = session['username']
    if picid is None and latest_favorite is None:
        r = {"error": "You did not provide an id and username parameter.", "status": 404}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response
    if picid is None:
        r = {"error": "You did not provide an id parameter.", "status": 404}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response
    if latest_favorite is None:
        r = {"error": "You did not provide a username parameter.", "status": 404}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 404
        db.close()
        return response

    query = "SELECT * FROM Photo WHERE picid = '%s'" %picid
    valid_pic = execute(query, db)
    if len(valid_pic) == 0:
        r = {"error": "Invalid id. The picid does not exist.", "status": 422}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 422
        db.close()
        return response

    query = "SELECT * FROM User WHERE username = '%s'" % latest_favorite
    user = execute(query, db)
    if len(user) == 0:
        r = {"error": "Invalid username. The username does not exist.", "status": 422}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 422
        db.close()
        return response

    query = "SELECT * FROM Favorite WHERE username = '%s' and picid = '%s'" % (latest_favorite, picid)
    fav_user = execute(query, db)
    if len(fav_user) > 0:
        r = {"error": "The user has already favorited this photo.", "status": 403}
        ast.literal_eval(json.dumps(r))
        response = jsonify(r)
        response.status_code = 403
        db.close()
        return response

    query = "INSERT INTO Favorite(picid, username) VALUES('%s', '%s');" % (picid, latest_favorite)
    update(query, db)
    response = jsonify(id=picid, status=201)
    response.status_code = 201
    db.close()
    return response

###############################################################################

@app.route('/ofvujvy4x6r/pa4/search', methods=['GET', 'POST'])
def search():
    db = MySQLdb.connect(db="group73", user="group73", passwd="iamtheshit", \
        cursorclass=MySQLdb.cursors.DictCursor)
    # db = MySQLdb.connect(db="test", cursorclass=MySQLdb.cursors.DictCursor)
    if request.form.get('op') == 'similar':
        return request.form.get('query')
    if request.form.get('op') == 'search':
        c = db.cursor()
        QUERY = request.form.get('query')
        result = requests.get('http://localhost:6273/search?q=%s' % QUERY)
        data = result.json()
        # return json.dumps(data)
        photos = list(dict())
        for each in data['hits']:
            sql = "SELECT sequencenum, url, caption FROM Photo WHERE sequencenum=%s" % each['id']
            photo = sql_query(sql, c);
            photos.append(photo[0])

        c.close()
        db.close()
        return render_template("search.html", result=photos, length=len(photos)) 
    db.close()
    return render_template("search.html") 

###############################################################################

if __name__ == '__main__':
    # listen on external IPs
    app.run(host='eecs485-08.eecs.umich.edu', port=5673, debug=True)
    # app.run(host='localhost', port=5673, debug=True)
