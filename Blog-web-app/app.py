from flask import Flask, flash, render_template, request, redirect, session, url_for
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
@app.route('/home')
def dashboard():
    if 'logged_in' in session:
        return render_template('home.html')
    else:
        return redirect('/login')

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
def home():
    if 'logged_in' in session:
        flash({session["username"]})
    else:
        return redirect('/login')
 
@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/userprofile')
def userprofile():
    username = session.get('username')
    if username:
        user = SomeUser.query.filter_by(username = username).first()
        if user:
            users = SomeUser.query.all()
            return render_template('userprofile.html',name = user.name,username=user.username,email=user.email,phone=user.phone,gender=user.gender)
        else:
            return "User not found"
    else:
        return "No username found in session"

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged out")
    return redirect(url_for('logout_page'))

@app.route('/logout_page')
def logout_page():
    return render_template('logout.html')

@app.route('/editprofile')
def editprofile():
    username = session.get('username')
    if username:
        user = SomeUser.query.filter_by(username = username).first()
        if user:
            users = SomeUser.query.all()
            return render_template('editprofile.html',name = user.name,username=user.username,email=user.email,phone=user.phone,gender=user.gender)
        else:
            return "User not found"
    else:
        return "No username found in session"

@app.route('/submit_edit', methods=["POST"])
def submit_edit():
    username = session.get('username')
    if username:
        user = SomeUser.query.filter_by(username=username).first()
        if user:
            user.name = request.form['name']
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone = request.form['phone']
            user.gender = request.form['gender']

            # Only update the password if a new one is provided
            new_password = request.form['password']
            if new_password:
                user.password = generate_password_hash(new_password)
                
            db.session.commit()
            return redirect('/userprofile')
    return "User not found or not logged in"

if __name__ == '__main__':
    app.run(debug=True)
