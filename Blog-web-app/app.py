import base64
from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



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
    phone = db.Column(db.String(10), unique=True, nullable=False)  
    gender = db.Column(db.String(10), nullable=True)

class BlogPost(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    heading_image = db.Column(db.String(255), nullable=False)
    first_paragraph = db.Column(db.Text, nullable=False)
    second_paragraph_image = db.Column(db.String(255), nullable=True)
    second_paragraph = db.Column(db.Text, nullable=False)
    third_paragraph_image = db.Column(db.String(255), nullable=True)
    third_paragraph = db.Column(db.Text, nullable=False)
    fourth_paragraph_image = db.Column(db.String(255), nullable=True)
    fourth_paragraph = db.Column(db.Text, nullable=False)
    fifth_paragraph_image = db.Column(db.String(255), nullable=True)
    fifth_paragraph = db.Column(db.Text, nullable=False)
    sixth_paragraph_image = db.Column(db.String(255), nullable=True)
    sixth_paragraph = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='blog_post', lazy=True)
    likes = db.relationship('Like', backref='blog_post', lazy=True)

    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    replies = db.relationship('Reply', backref='comment', lazy=True)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('some_user.id'), nullable=False)

with app.app_context():
    db.create_all()



@app.route('/home')
def dashboard():
    if 'logged_in' in session:
        if session['username'] != "proadmin":
            return render_template('home.html')
        elif session['username'] == "proadmin":
            return render_template('admindashboard.html')
    else:
        return redirect('/login')

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = SomeUser.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user.id
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
    if session['username'] != "proadmin":
        blog_posts = BlogPost.query.all()
        return render_template('blog.html', blog_posts=blog_posts)
    elif session['username'] == "proadmin":
        return render_template('admindashboard.html')

@app.route('/about')
def about():
    if session['username'] != "proadmin":
        return render_template('about.html')
    elif session['username'] == "proadmin":
        return render_template('admindashboard.html')

@app.route('/terms')
def terms():
    if session['username'] != "proadmin":
        return render_template('terms.html')
    elif session['username'] == "proadmin":
        return render_template('admindashboard.html')

@app.route('/userprofile')
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

@app.route('/logout')
def logout():
    session.clear()
    flash("You have successfully logged out")
    return redirect(url_for('logout_page'))

@app.route('/logout_page')
def logout_page():
    return render_template('logout.html')

@app.route('/admindashboard')
def admindashboard():
    if 'logged_in' in session and session['username'] =='proadmin':
        return render_template('admindashboard.html')
    elif session['username'] != 'proadmin':
        return render_template('home.html')


@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if session['username'] != 'proadmin':
        return render_template('blog_post.html', post=post)
    elif session['username'] == 'proadmin':
        return render_template('admindashboard.html')


@app.route('/addblog', methods=['GET', 'POST'])
def addblog():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        heading_image = request.files['heading_image'].read()
        first_paragraph = request.form['first_paragraph']
        second_paragraph_image = request.files['second_paragraph_image'].read()
        second_paragraph = request.form['second_paragraph']
        third_paragraph_image = request.files['third_paragraph_image'].read()
        third_paragraph = request.form['third_paragraph']
        fourth_paragraph_image = request.files['fourth_paragraph_image'].read()
        fourth_paragraph = request.form['fourth_paragraph']
        fifth_paragraph_image = request.files['fifth_paragraph_image'].read()
        fifth_paragraph = request.form['fifth_paragraph']
        sixth_paragraph_image = request.files['sixth_paragraph_image'].read()
        sixth_paragraph = request.form['sixth_paragraph']

        heading_image_base64 = base64.b64encode(heading_image).decode('utf-8')
        second_paragraph_image_base64 = base64.b64encode(second_paragraph_image).decode('utf-8')
        third_paragraph_image_base64 = base64.b64encode(third_paragraph_image).decode('utf-8')
        fourth_paragraph_image_base64 = base64.b64encode(fourth_paragraph_image).decode('utf-8')
        fifth_paragraph_image_base64 = base64.b64encode(fifth_paragraph_image).decode('utf-8')
        sixth_paragraph_image_base64 = base64.b64encode(sixth_paragraph_image).decode('utf-8')

        new_post = BlogPost(title=title, description=description, heading_image=heading_image_base64,
                            first_paragraph=first_paragraph, second_paragraph_image=second_paragraph_image_base64,
                            second_paragraph=second_paragraph, third_paragraph_image=third_paragraph_image_base64,
                            third_paragraph=third_paragraph, fourth_paragraph_image=fourth_paragraph_image_base64,
                            fourth_paragraph=fourth_paragraph, fifth_paragraph_image=fifth_paragraph_image_base64,
                            fifth_paragraph=fifth_paragraph, sixth_paragraph_image=sixth_paragraph_image_base64,
                            sixth_paragraph=sixth_paragraph)

        db.session.add(new_post)
        db.session.commit()

        return redirect('/home')
    if 'logged_in' in session and session['username'] == 'proadmin':
        return render_template('addblog.html')
    elif session['username'] != 'proadmin':
        return render_template('home.html')

@app.route('/viewblog')
def viewblog():
    blog_posts = BlogPost.query.all()
    if 'logged_in' in session and session['username'] == 'proadmin':
        return render_template('viewblog.html', blog_posts=blog_posts)
    elif session['username'] != 'proadmin':
        return render_template('home.html')

@app.route('/viewblog/<int:post_id>')
def editblog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('editblog.html', post=post)

@app.route('/update_blog/<int:post_id>', methods=['POST'])
def update_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    post.title = request.form['title']
    post.description = request.form['description']
    post.first_paragraph = request.form['first_paragraph']
    post.second_paragraph = request.form['second_paragraph']
    post.third_paragraph = request.form['third_paragraph']
    post.fourth_paragraph = request.form['fourth_paragraph']
    post.fifth_paragraph = request.form['fifth_paragraph']
    post.sixth_paragraph = request.form['sixth_paragraph']

    if 'heading_image' in request.files and request.files['heading_image'].filename != '':
        heading_image = request.files['heading_image'].read()
        post.heading_image = base64.b64encode(heading_image).decode('utf-8')
    if 'second_paragraph_image' in request.files and request.files['second_paragraph_image'].filename != '':
        second_paragraph_image = request.files['second_paragraph_image'].read()
        post.second_paragraph_image = base64.b64encode(second_paragraph_image).decode('utf-8')
    if 'third_paragraph_image' in request.files and request.files['third_paragraph_image'].filename != '':
        third_paragraph_image = request.files['third_paragraph_image'].read()
        post.third_paragraph_image = base64.b64encode(third_paragraph_image).decode('utf-8')
    if 'fourth_paragraph_image' in request.files and request.files['fourth_paragraph_image'].filename != '':
        fourth_paragraph_image = request.files['fourth_paragraph_image'].read()
        post.fourth_paragraph_image = base64.b64encode(fourth_paragraph_image).decode('utf-8')
    if 'fifth_paragraph_image' in request.files and request.files['fifth_paragraph_image'].filename != '':
        fifth_paragraph_image = request.files['fifth_paragraph_image'].read()
        post.fifth_paragraph_image = base64.b64encode(fifth_paragraph_image).decode('utf-8')
    if 'sixth_paragraph_image' in request.files and request.files['sixth_paragraph_image'].filename != '':
        sixth_paragraph_image = request.files['sixth_paragraph_image'].read()
        post.sixth_paragraph_image = base64.b64encode(sixth_paragraph_image).decode('utf-8')

    db.session.commit()
    return redirect(url_for('viewblog'))

@app.route('/delete_blog/<int:post_id>', methods=['POST'])
def delete_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('viewblog'))

@app.route('/edituser')
def edituser():
    users = SomeUser.query.all()
    if 'logged_in' in session and session['username'] == 'proadmin':
        return render_template('edituser.html', users=users)
    elif session['username'] != 'proadmin':
        return render_template('home.html')

@app.route('/edituser/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = SomeUser.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.username = request.form['username']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.gender = request.form['gender']
        
        new_password = request.form['password']
        if new_password:
            user.password = generate_password_hash(new_password)
        
        db.session.commit()
        return redirect(url_for('edituser'))
    
    return render_template('edit_user_form.html', user=user)

@app.route('/deleteuser/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = SomeUser.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('edituser'))

if __name__ == '__main__':
    app.run(debug=True)
