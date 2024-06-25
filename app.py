from flask import Flask, url_for, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'GET':
        return render_template('create_post.html')
    else:
        category_name = request.form['category']
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()
        post = Post(title=request.form['title'], body=request.form['body'], category=category)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/edit_post/<int:post_id>', methods=['GET'])
def edit_post(post_id):
    post = Post.query.get(post_id)  # Assuming 'Post' is your model
    if post:
        return render_template('edit_post.html', post=post)
    return redirect(url_for('index'))

@app.route('/update_post/<int:post_id>', methods=['POST'])
def update_post(post_id):
    post = Post.query.get(post_id)
    if post:
        post.title = request.form['title']
        post.body = request.form['body']
        # Update the category if your model supports direct updates like this
        post.category.name = request.form['category']
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    return redirect(url_for('index'))



@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()  # Create the database tables
    app.run(debug=True)
