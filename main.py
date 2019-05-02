from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:wakacje10@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    password = db.Column(db.String(15))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else: 
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if user and user.password != password:
            flash("Incorrect password")
            return redirect('/login')
        if not user:
            flash("Username does not exist")
            return redirect('/login')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if username == "" or password == "" or verify == "":    
                flash("One or more fields are invalid")
                return redirect('/signup')
            elif len(username) < 3 or len(username) > 15:     
                flash("This is not a valid username")
                return redirect('/signup')
            elif len(password) < 3 or len(password) > 15:
                flash("This is not a valid password")
                return redirect('/signup')
            elif password != verify:
                flash("The password do not match")
                return redirect('/signup')
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
        else:
            flash("Username already exists")
            return redirect('/signup')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template("newpost.html")

    else:
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        user_id = request.args.get('user')

        title_error = request.args.get("title_error")
        body_error = request.args.get("body_error")

        title_error = ""
        body_error = ""
        
        if title == '':
            title_error = "Please fill in the title"
        
        if body == '':
            body_error = "Please fill in the body"

        if not title_error and not body_error:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            blog = Blog.query.filter_by(id=new_post.id).first()
            user = User.query.filter_by(id = user_id).first()
            return render_template("post.html", blog=blog, user=user)
        
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)


@app.route('/blog')
def blog():
    blog_posts = Blog.query.all()
    
    user_id = request.args.get('user')
    post_id = request.args.get('id')
    blog = Blog.query.filter_by(id = post_id).first()
    user_posts = Blog.query.filter_by(owner_id = user_id).all()
    user = User.query.filter_by(id = user_id).first()
    if post_id:
        return render_template("post.html", blog=blog, user=user)
    if user_id:
        return render_template("user_page.html", user_posts=user_posts, blog=blog, user=user)    
    else:
        return render_template('blog.html', blog_posts = blog_posts, user=user, blog=blog)


@app.route('/')
def index():
    users = User.query.all()
    return render_template("index.html", users=users)



if __name__ == '__main__':
    app.run()