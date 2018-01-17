from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1028))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def main_page():
    blogs = Blog.query.all()
    blog_id = request.args.get('id')
    return render_template('blog.html',title="Build a Blog", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def index():
    title_error=""
    body_error=""
    if request.method == 'POST':
        blog_name = request.form['blog']
        body_name = request.form['body']
        if blog_name == "":
            title_error="Please fill out the title"
        if body_name =="":
            body_error="Please fill out the body"
        if not title_error and not body_error:
            new_blog = Blog(blog_name, body_name)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = request.args.get('id')
            return redirect('/post')

        else:
            return render_template('newpost.html',title="Build a Blog", blog_name=blog_name,title_error=title_error,body_name=body_name, body_error=body_error)

    blogs = Blog.query.all()
    return render_template('newpost.html',title="Build a Blog", blogs=blogs, title_error="",body_error="")



@app.route('/post', methods=['POST', 'GET'])
def read_posts():
    blog_id = request.args.get('id')
    r_post = Blog.query.get(blog_id)
    return render_template('post.html',title="Build a Blog", r_post=r_post)

if __name__ == '__main__':
    app.run()