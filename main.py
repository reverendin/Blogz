from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = '3aaY299kbPQX'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5140))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120),unique = True)
    pw_hash = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.pw_hash = make_pw_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    user_id = request.args.get('id')
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET'])
def main_page():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    return render_template('blog.html', blogs=blogs)

@app.route('/singleUser', methods=['GET'])
def single_user():
    #owner = User.query.filter_by(email=session['email']).first()
    user_id = request.args.get('id')
    blogs = Blog.query.filter_by(owner_id=user_id).all()
    return render_template('singleUser.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title_error=""
    body_error=""
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        blog_name = request.form['blog']
        body_name = request.form['body']
        if blog_name == "":
            title_error="Please fill out the title"
        if body_name =="":
            body_error="Please fill out the body"
        if not title_error and not body_error:
            new_blog = Blog(blog_name, body_name, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/post?id={}'.format(blog_id))

        else:
            return render_template('newpost.html', blog_name=blog_name,title_error=title_error,body_name=body_name, body_error=body_error)

    blogs = Blog.query.all()
    return render_template('newpost.html', blogs=blogs, title_error="",body_error="")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            return redirect('/blog')
        else:
            flash('User and password combination does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(email=email).first()
        if password == verify:
            if not existing_user:
                new_user = User(name, email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/blog')
            else:
                flash('User already exists', 'error')
        else:
            flash('Passwords do not match', 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/post', methods=['POST', 'GET'])
def read_posts():
    blog_id = request.args.get('id')
    r_post = Blog.query.get(blog_id)
    return render_template('post.html', r_post=r_post)

if __name__ == '__main__':
    app.run()