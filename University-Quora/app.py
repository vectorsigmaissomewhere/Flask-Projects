import base64
from functools import wraps
from flask import Flask, flash, render_template,request,redirect,session, url_for
import flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app=Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///universityquora.db'
db = SQLAlchemy(app)

class SomeUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)  
    gender = db.Column(db.String(10), nullable=True)
    questions = db.relationship('Question', backref='author', lazy=True)
    question_comments = db.relationship('QuestionComment', backref='author', lazy=True)
    question_votes = db.relationship('QuestionVote', backref='voter', lazy=True)
    comment_votes = db.relationship('CommentVote', backref='voter', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('QuestionComment', backref='question', lazy=True)
    votes = db.relationship('QuestionVote', backref='question', lazy=True)

    def vote_count(self):
        return sum(vote.vote for vote in self.votes)

class QuestionComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.relationship('CommentVote', backref='comment', lazy=True)

class QuestionVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    vote = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote

class CommentVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('question_comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    vote = db.Column(db.Integer, nullable=False)  # 1 for upvote, -1 for downvote

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(15), nullable=False) 
    message = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != 'proadmin':
            flash("You do not have permission to access the admin panel.")
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in session and session['username'] == 'proadmin':
            flash("Admin cannot access regular user pages.")
            return redirect(url_for('admindashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        phonenumber = request.form['phone']
        gender = request.form['gender']

        new_user = SomeUser(name=name,username=username,email=email,password=hashed_password,phone=phonenumber,gender=gender)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    msg = "You have successfully logged in"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = SomeUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user.id
            flash("You have successfully logged in")
            return redirect(url_for('home'))
        else:
            return 'Inavlid username or password. Please try again.'
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged out", "info")
    return redirect(url_for('login'))

@app.route('/home')
@user_required
def home():
    search_results = Question.query.order_by(Question.timestamp.desc()).limit(6).all()
    return render_template('home.html',questions=search_results)

@app.route('/about')
@user_required
def about():
    return render_template('about.html')

@app.route('/quora', methods=['GET'])
@user_required
def quora():
    search_query = request.args.get('search_query', '')
    if search_query:
        search_results = Question.query.filter(Question.tags.contains(search_query)).order_by(Question.timestamp.desc()).limit(10).all()
    else:
        search_results = Question.query.order_by(Question.timestamp.desc()).limit(10).all()
    return render_template('quora.html', questions=search_results, search_query=search_query)



@app.route('/addquora', methods=['GET', 'POST'])
@user_required
def addquora():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tag']
        user_id = session.get('user_id')

        if user_id is None:
            flash("You need to be logged in to add a question")
            return redirect(url_for('login'))

        new_question = Question(user_id=user_id, title=title, description=description, tags=tags)
        db.session.add(new_question)
        db.session.commit()

        flash("Question added successfully")
        return redirect(url_for('quora'))

    return render_template('addquora.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
@user_required
def question_detail(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        if 'logged_in' not in session:
            flash("You need to be logged in to comment or vote.", "error")
            return redirect(url_for('login'))

        user_id = session['user_id']
        if 'comment' in request.form:
            content = request.form['comment']
            new_comment = QuestionComment(question_id=question_id, user_id=user_id, content=content)
            db.session.add(new_comment)
            db.session.commit()
            flash("Comment added successfully", "success")
        elif 'vote' in request.form:
            vote_type = int(request.form['vote'])
            vote = QuestionVote.query.filter_by(question_id=question_id, user_id=user_id).first()
            if vote:
                vote.vote = vote_type
            else:
                vote = QuestionVote(question_id=question_id, user_id=user_id, vote=vote_type)
                db.session.add(vote)
            db.session.commit()
            flash("Vote recorded", "success")
        return redirect(url_for('question_detail', question_id=question_id))

    comments = QuestionComment.query.filter_by(question_id=question_id).all()
    return render_template('question_detail.html', question=question, comments=comments)

@app.route('/userprofile')
@user_required
def userprofile():
    username = session.get('username')
    if username:
        user = SomeUser.query.filter_by(username = username).first()
        if user:
            users = SomeUser.query.all()
            if session['username'] != "proadmin":
                return render_template('userprofile.html',name = user.name,username=user.username,email=user.email,phone=user.phone,gender=user.gender)
            elif session['username'] == "proadmin":
                return render_template('admindashboard.html')
        else:
            return "User not found"
    else:
        return "No username found in session"

@app.route('/editprofile')
@user_required
def editprofile():
    username = session.get('username')
    if username:
        user = SomeUser.query.filter_by(username = username).first()
        if user:
            users = SomeUser.query.all()
            if session['username'] != "proadmin":
                return render_template('editprofile.html',name = user.name,username=user.username,email=user.email,phone=user.phone,gender=user.gender)
            elif session['username']  == "proadmin":
                return render_template('admindashboard.html')
        else:
            return "User not found"
    else:
        return "No username found in session"

@app.route('/submit_edit', methods=["POST"])
@user_required
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

            new_password = request.form['password']
            if new_password:
                user.password = generate_password_hash(new_password)
                
            db.session.commit()
            return redirect('/userprofile')
    return "User not found or not logged in"

"""for Contact"""
@app.route('/contact', methods=['GET', 'POST'])
@user_required
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        new_contact = Contact(name=name, email=email, number=phone, message=message)
        db.session.add(new_contact)
        db.session.commit()
        flash("Message sent successfully", "success")
        return redirect('/about')

    return render_template('contact.html')


"""======================================="""
"""=======CREATING ROUTES FOR ADMIN======="""
@app.route('/admindashboard')
@admin_required
def admindashboard():
    return render_template('admindashboard.html')

"""
<li><a href="{{ url_for('admindashboard') }}">Admin<br>Dashboard</a></li>
            <li><a href="{{ url_for('manageuser') }}">manage<br>user</a></li>
            <li><a href="{{ url_for('managequora') }}">manage<br>quora</a></li>
"""


@app.route('/manageuser')
@admin_required
def manageuser():
    if 'logged_in' in session and session.get('username') == 'proadmin':
        users = SomeUser.query.all()
        return render_template('manageuser.html', users=users)
    else:
        return redirect(url_for('login'))


"""here we cannot delete the user as we need to delete the quora too
so what I will do is delete the user and the quora related to it
"""
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = SomeUser.query.get_or_404(user_id)
    
    QuestionComment.query.filter_by(user_id=user_id).delete()
    questions = Question.query.filter_by(user_id=user_id).all()
    for question in questions:
        QuestionComment.query.filter_by(question_id=question.id).delete()
        QuestionVote.query.filter_by(question_id=question.id).delete()
        db.session.delete(question)
    db.session.delete(user)
    db.session.commit()
    
    return redirect(url_for('manageuser'))


@app.route('/managequora')
@admin_required
def managequora():
    return render_template('managequora.html')

@app.route('/adminquora', methods=['GET'])
@admin_required
def adminquora():
    search_query = request.args.get('search_query', '')
    search_results = Question.query.filter(Question.tags.contains(search_query)).order_by(Question.timestamp.desc()).limit(10).all()
    return render_template('managequora.html', questions=search_results)

@app.route('/deletequestion/<int:question_id>', methods=['POST'])
@admin_required
def deletequestion(question_id):
    question = Question.query.get_or_404(question_id)
    QuestionComment.query.filter_by(question_id=question.id).delete()
    QuestionVote.query.filter_by(question_id=question.id).delete()
    
    db.session.delete(question)
    db.session.commit()
    
    return redirect(url_for('adminquora'))


if __name__ =='__main__':
    app.run(debug=True)

