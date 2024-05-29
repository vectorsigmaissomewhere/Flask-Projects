import base64
from flask import Flask
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

with app.app_context():
    db.create_all()

if __name__ =='__main__':
    app.run(debug=True)
