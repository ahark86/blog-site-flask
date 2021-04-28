from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, URL, email, length
import os
import helper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_for_now'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    subtitle = db.Column(db.String(500))
    publish_date = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(500), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commented_by = db.Column(db.String(100), nullable=False)
    comment_title = db.Column(db.String(100), nullable=False)
    comment_date = db.Column(db.String, nullable=False)
    comment_body = db.Column(db.Text, nullable=False)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_title = db.Column(db.String(20), nullable=False)


db.create_all()


# Form Objects
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle (Optional)")
    img_url = StringField("Blog Post Image Url", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Post Body", validators=[DataRequired()])
    submit = SubmitField("Post")


class CreateUserForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), email()])
    password = PasswordField("Password", validators=[DataRequired(), length(min=8, max=20)])


# Routes
@app.route('/')
def recent_posts():
    recent_posts = db.session.query(BlogPost).order_by(BlogPost.id.desc()).limit(3)
    all_tags = db.session.query(Tag).all()
    return render_template('index.html', posts=recent_posts, all_tags=all_tags, recent=True)


@app.route('/all-posts')
def all_posts():
    all_posts = db.session.query(BlogPost).order_by(BlogPost.id.desc()).all()
    all_tags = db.session.query(Tag).all()
    return render_template('index.html', posts=all_posts, all_tags=all_tags, all=True)


@app.route("/create-post", methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        img_url = request.form['img_url']
        body = request.form['body']
        publish_date = helper.render_date()
        author = "Alex Harker"

        new_post = BlogPost(title=title,
                            subtitle=subtitle,
                            img_url=img_url,
                            body=body,
                            author=author,
                            publish_date=publish_date)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('recent_posts'))

    return render_template('create-post.html', form=form)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post_to_show = BlogPost.query.get(post_id)
    return render_template("index.html", post=post_to_show, show=True)


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("recent_posts"))


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = BlogPost.query.get(post_id)
    title = post_to_edit.title
    subtitle = post_to_edit.subtitle
    img_url = post_to_edit.img_url
    body = post_to_edit.body
    form = CreatePostForm(title=title,
                          subtitle=subtitle,
                          img_url=img_url,
                          body=body)

    if request.method == 'POST':
        new_title = request.form['title']
        new_subtitle = request.form['subtitle']
        new_img_url = request.form['img_url']
        new_body = request.form['body']

        post_to_edit.title = new_title
        post_to_edit.subtitle = new_subtitle
        post_to_edit.img_url = new_img_url
        post_to_edit.body = new_body

        db.session.commit()

        return redirect(url_for('all_posts'))

    return render_template('edit-post.html', form=form, post=post_to_edit)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
