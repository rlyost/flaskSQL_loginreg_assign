from flask import Flask, request, redirect, render_template, session, flash
import datetime
import re
import md5
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'rangersleadtheway'
mysql = MySQLConnector(app,'logreg')

@app.route('/')
def index():
    # query = "SELECT * FROM users"                           # define your query
    # users = mysql.query_db(query)                           # run query with query_db()
    return render_template('index.html') # pass data to our template

@app.route('/registration', methods=['POST'])
def registration():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['regemail']
    hashed_password = md5.new(request.form['regpassword']).hexdigest()
    password2 = request.form['regpassword2']

    # Write query as a string.
    # we want to insert into our Db.
    query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :regemail, :hashed_password, NOW(), NOW());"
    # query data for email validation
    query_val = "SELECT email FROM users WHERE email = :regemail;"
 
   # We'll then create a dictionary of data from the POST data received.
    data = {
            'fname': request.form['fname'],
            'lname':  request.form['lname'],
            'regemail': request.form['regemail'],
            'hashed_password': hashed_password
           }
    check = mysql.query_db(query_val, data)
    
    # Check name fields
    if len(fname) < 2 or len(lname) < 2:
        flash("Name must be longer.")
        return redirect('/')
    elif not str(fname).isalpha():
        flash("First Name can only be letters.")
        return redirect('/')       
    elif not str(lname).isalpha():
        flash("Last Name can only be letters.")
        return redirect('/')
    
    # Validates email address for proper format.
    if len(email) < 1:
        flash("Email cannot be blank!")
        return redirect('/')
    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email Address!")
        return redirect('/')
    elif len(check) != 0:
        flash("Duplicate address, enter another one!")
        return redirect('/')
    
    # Check password length and confirmation
    if len(request.form['regpassword']) < 8:
        flash("Password is not long enough!")
        return redirect('/')
    elif request.form['regpassword'] != password2:
        flash("Passwords do not match!")
        return redirect('/')

    # Run query, with dictionary values injected into the query.
    mysql.query_db(query, data)
    session['from'] = 0
    return redirect('/success')

@app.route('/success')
def success():
    if session['from'] == 1:
        flash("Welcome Back!  You have successfully logged in!")
    else:
        flash("Welcome!  You have successfully registered on our site!")
    return render_template('success.html')

@app.route('/login', methods=['POST'])
def login():
    query = "SELECT email FROM users WHERE email = :logemail;"
    query_pw = "SELECT password FROM users WHERE email = :logemail;"
    hashed_password = md5.new(request.form['logpassword']).hexdigest()
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'logemail': request.form['logemail'],
             'logpassword': request.form['logpassword']
           }
    
    # query for email validation
    check = mysql.query_db(query, data)
    # query for password validation
    check_pw = mysql.query_db(query_pw, data)

    # Validates email address for proper format.
    if len(request.form['logemail']) < 1:
        flash("Email cannot be blank!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['logemail']):
        flash("Invalid Email Address!")
        return redirect('/')
    elif len(check) == 0:
        flash("Email not found!")
        return redirect('/')

    #password validation
    if hashed_password != check_pw[0]['password']:
        flash("Password does not match.")
        return redirect('/')

    session['from'] = 1
    return redirect('/success')

app.run(debug=True)