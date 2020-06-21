from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, jsonify
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, IntegerField, FloatField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from dataset import Crdata

app = Flask(__name__)

# Config MySQl
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysqleight'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

# Index
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Articles
@app.route('/articles')
def articles():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
            return render_template('articles.html', articles = articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg = msg)

    # Close connection
    cur.close()

# Single Article
@app.route('/article/<id>/')
def article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    return render_template('article.html', article = article)

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min = 1, max = 50)])
    lastname = StringField('Last Name', [validators.Length(min = 4, max = 25)])
    email = StringField('Email', [validators.Length(min = 6, max = 50), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        lastname = form.lastname.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, lastname, password) VALUES(%s, %s, %s, %s)", (name, email, lastname, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'Success')

        return redirect(url_for('login'))

    return render_template('register.html', form = form)


# User Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create cursor 
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['email'] = email

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error = error)
            # Close connection
            cur.close()
        else:
            error = 'Email not found'
            return render_template('login.html', error = error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unautohorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# Evaluation Form Class
class EvaluationForm(Form):
    conditions = StringField('Condition', [validators.Length(min = 3, max = 30)])
    districts = StringField('District', [validators.Length(min = 3, max = 30)])
    max_floors = IntegerField('Max Floor', [validators.Length(min = 1, max = 3)])
    streets = StringField('street', [validators.Length(min = 3, max = 40)])
    num_rooms = IntegerField('Number of Rooms', [validators.Length(min = 1, max = 3)])
    areas = IntegerField('Area', [validators.Length(min = 1, max = 5)])
    building_types = StringField('Building Type', [validators.Length(min = 3, max = 30)])
    floors = IntegerField('Floor', [validators.Length(min = 1, max = 3)])
    ceiling_heights = FloatField('Ceiling Height', [validators.Length(min = 1, max = 10)])
    answer = IntegerField('Answer', [validators.Length(min=5, max=7)])


# Get House Parameters
@app.route('/get/values', methods = ['GET', 'POST'])
@is_logged_in
def get_values():
    
    form = EvaluationForm(request.form)
    
    datas = Crdata()
    form.streets = datas.columns_name('streets')
    form.districts = datas.columns_name('districts')
    form.max_floors = datas.columns_name('max_floor')
    form.conditions = datas.columns_name('conditions')
    form.num_rooms = datas.columns_name('num_rooms')
    form.building_types = datas.columns_name('building_type')
    form.ceiling_heights = datas.columns_name('ceiling_height')
    form.floors = datas.columns_name('max_floor')
    
    return render_template('evaluation.html',  form = form)
  

# Evaluation
@app.route('/evaluation', methods = ['POST'])
@is_logged_in
def evaluation():

    response = request.get_json()

    # Create object
    datas = Crdata()

    house_price = datas.evaluation(response['district'], response['street'], response['maxFloor'], response['buildingType'], response['areas'], response['condition'], response['floor'], response['numRooms'], response['ceilingHeight'])

    if house_price < 0:
        return jsonify("Oops!!! House with such parameters doesn't exist.")
    else:
        return jsonify("Your perfect house PRICE is ${} (± $250)".format(house_price))

# Dashboard
@app.route('/dashboard', methods = ['GET', 'POST'])
@is_logged_in
def dashboard():


    # Create cursor
    cur = mysql.connection.cursor()

    # Get articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
            return render_template('dashboard.html', articles = articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg = msg)

    # Close connection
    cur.close()


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min = 1, max = 200)])
    body = TextAreaField('Body', [validators.Length(min = 30)])
    
# Add Article
@app.route('/add_article', methods = ['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['email']))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form = form)

# Edit Article
@app.route('/edit_article/<id>', methods = ['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Execute
        cur.execute("UPDATE articles SET title = %s, body = %s WHERE id = %s", (title, body, id))

        # Commit to DB
        mysql.connection.commit()

        # Close Connection
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form = form)


# Delete Article
@app.route('/delete_article/<id>', methods = ['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    # Commit to DB
    mysql.connection.commit()

    # Close Connection
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(use_reloader = True, debug = True)