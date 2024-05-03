from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)




# Creating a user model
"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)  # Ensure this line is present
    gender = db.Column(db.String(10), nullable=True)
"""
class SomeUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)  # Ensure this line is present
    gender = db.Column(db.String(10), nullable=True)
# creating a database within the application context 
with app.app_context():
    db.create_all()



# creating route for Home page
@app.route('/')
def home():
    return render_template('home.html')

# creating route for Register Page
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'] 
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        phonenumber = request.form['phone']
        gender = request.form['gender']

        new_user = SomeUser(name=name, username=username, email=email, password=hashed_password, phone=phonenumber, gender=gender)      
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')  
    
    return render_template('register.html')

# creating a route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = SomeUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect('/home')
        else:
            return 'Invalid username or password. Please try again.'
    
    return render_template('login.html')

@app.route('/home')
def index():
    if 'logged_in' in session:
        return f'Welcome, {session["username"]}! This is your dashboard.'
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)

