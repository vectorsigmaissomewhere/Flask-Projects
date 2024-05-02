from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)




# Creating a user model
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
    return render_template('index.html')

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
@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
