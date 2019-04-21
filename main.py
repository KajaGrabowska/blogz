from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:wakacje@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template("newpost.html")

    else:
        title = request.form['title']
        body = request.form['body']

        title_error = request.args.get("title_error")
        body_error = request.args.get("body_error")

        title_error = ""
        body_error = ""
        
        if title == '':
            title_error = "Please fill in the title"
        
        if body == '':
            body_error = "Please fill in the body"

        if not title_error and not body_error:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/blog")
        
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, body=body)



@app.route('/post')
def display_post():
    return render_template("post.html")




@app.route('/blog')
def blog():
    blog_posts = Blog.query.all()
    
    
    post_id = request.args.get('id')
    blog = Blog.query.filter_by(id = post_id).first()
    if post_id != None:
        return render_template("post.html", blog_posts = blog_posts, blog=blog)
    else:
    #completed_tasks = Task.query.filter_by(completed=True).all()
        return render_template('blog.html', blog_posts = blog_posts)



if __name__ == '__main__':
    app.run()