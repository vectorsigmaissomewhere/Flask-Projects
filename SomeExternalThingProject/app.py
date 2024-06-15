from functools import wraps
from flask import Flask, flash, render_template,request,redirect,session,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import  datetime
import json
import os
import hashlib

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session or session['email'] != 'Admin@Gmail.Com':
            flash("You do not have permission to access the admin panel.")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in session and session['email'] == 'Admin@Gmail.Com':
            flash("Admin cannot access regular user pages.")
            return redirect(url_for('admindashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============================= WORKING ON CREDENTIALS =============================================
class User:
    def __init__(self, fullname, email, number, password, securitynumber, filename='user.json'):
        self.fullname = fullname
        self.email = email
        self.number = number
        self.password = password
        self.securitynumber = securitynumber
        self.filename = filename
        self.save_user()

    # Searching for email address if it exists or not 
    """
    def search_email(filename,email):
        try:
            with open(filename,'r') as file:
                data = json.load(file)
                if not isinstance(data,list):
                    raise ValueError("JSON data is not a list")
        except (FileNotFoundError,json.JSONDecodeError) as e:
            print(f"Errror loading JSON file: {e}")
            return None
        
        for email in data:
            if email.get("email") == email:
                return email
        
        return None
    """
    def save_user(self):
        user_dict = {
            "fullname": self.fullname,
            "email": self.email,
            "number": self.number,
            "password": self.password,
            "securitynumber": self.securitynumber
        }

        #checkemail = search_email(self.filename,self.email)
        #if checkemail:
        #    return render_template('error.html')

        # read existing data, as if the data is avaiable or not
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # addding a new data
        data.append(user_dict)

        # writing the new data into json file
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)


# ========================= Hackathon model
class Hackathon:
    def __init__(self, title, description, start_date, end_date):
        self.title = title
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    @staticmethod
    def from_dict(hackathon_dict):
        return Hackathon(hackathon_dict['title'], hackathon_dict['description'],
                         hackathon_dict['start_date'], hackathon_dict['end_date'])

    def matches_title(self, title):
        return self.title == title

def load_hackathons():
    try:
        with open('hackathons.json', 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return [Hackathon.from_dict(hackathon) for hackathon in data]
            else:
                return []
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading hackathons: {e}")
        return []

def save_hackathons(hackathons):
    with open('hackathons.json', 'w') as file:
        json.dump([hackathon.to_dict() for hackathon in hackathons], file, indent=4)

def find_hackathon_by_title(title):
    hackathons = load_hackathons()
    for hackathon in hackathons:
        if hackathon.matches_title(title):
            return hackathon
    return None

def delete_hackathon_by_title(title):
    hackathons = load_hackathons()
    updated_hackathons = [hackathon for hackathon in hackathons if not hackathon.matches_title(title)]
    save_hackathons(updated_hackathons)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['name']
        email = request.form['email']
        number = request.form['phone']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        securitynumber = request.form['securitynumber']
        user = User(fullname, email, number, hashed_password, securitynumber)
        print("User has been added")
    return render_template('register.html')
 
# ==========================================WORKING FOR LOGIN=====================
# searching for the email address
def search_email(emailid):
    try:
        with open('user.json', 'r') as file:
            data = json.load(file)
        for user in data:
            if user['email'] == emailid:
                return user
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None

# searching for the password
def search_password(password):
    hashed_password = generate_password_hash(password)
    with open('user.json', 'r') as file:
        data = json.load(file)
    allcredentiallist = []
    for j in data:
        for key,value in j.items():
            allcredentiallist.append(value)
    found = False
    # searching for the hashed password if it exists
    for i in allcredentiallist:
        if check_password_hash(i) == password:
            found = True
    return found

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = search_email(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = user['email']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' in session:
        hackathons = load_hackathons()
        return render_template('home.html', hackathons=hackathons)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

#===============================admin=======================================
@app.route('/admindashboard')
@admin_required
def admindashboard():
    return render_template('admindashboard.html')
#==============adding hackathon
# Function to load hackathons from JSON file
@app.route('/addhackathon', methods=['GET', 'POST'])
@admin_required
def addhackathon():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        if title and description and start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')

                hackathon = Hackathon(title, description, start_date, end_date)
                hackathons = load_hackathons()
                hackathons.append(hackathon)
                save_hackathons(hackathons)

                print(f"Added hackathon: {hackathon.title}")
                return redirect(url_for('viewhackathon'))
            except ValueError as e:
                print(f"Error adding hackathon: {e}")

    return render_template('addhackathon.html')

@app.route('/viewhackathon', methods=['GET', 'POST'])
@admin_required
def viewhackathon():
    if request.method == 'POST':
        title = request.form['title']
        hackathon = find_hackathon_by_title(title)
        if hackathon:
            return render_template('viewhackathon.html', hackathon=hackathon)
        else:
            return render_template('viewhackathon.html', error='Hackathon not found')
    return render_template('viewhackathon.html')

@app.route('/deletehackathon', methods=['POST'])
@admin_required
def delete_hackathon():
    title = request.form['title']
    delete_hackathon_by_title(title)
    return redirect(url_for('viewhackathon'))


if __name__ == '__main__':
    app.run(debug=True)
