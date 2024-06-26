import secrets
import os
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for Matplotlib
import matplotlib.pyplot as plt
import io
from PIL import Image
from flask import render_template, url_for,request ,flash, redirect, abort, Response
from budget_app import app, db, bcrypt
from budget_app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, SubPostForm
from budget_app.models import User, Post, Subpost
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
def first_page():
    return render_template('first_page.html')


@app.route("/home")
def home():
    posts = Post.query.filter(Post.user_id == current_user.id).all()

    return render_template('home.html', title='Your post', posts=posts)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
         return redirect('home')
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
         return redirect('home')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember = form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home')) 
        else :  
            flash('Login Unsuccessful. Please check Email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
     logout_user()
     return redirect(url_for('first_page')) 

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images',picture_fn)
    
    new_size = (125,125)
    ig = Image.open(form_picture)
    ig.thumbnail(new_size)
    ig.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():

    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash ('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
         form.username.data = current_user.username
         form.email.data = current_user.email

    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form = form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content = form.content.data, price = form.price.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post as been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form = form, legend = 'New post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    subposts = Subpost.query.filter(Subpost.post_id == post.id).all()
    value_subpost = 0
    for item in subposts :
        value_subpost -= item.price
    total_post = float(post.price) - value_subpost
    if post.author != current_user:
        abort(403)
    return render_template('post.html', title=post.title , post = post, subposts=subposts, total = total_post)



@app.route("/post/<int:post_id>/update",  methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.price = form.price.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id = post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.price.data = post.price


    form.title.data = post.title
    form.content.data = post.content
    form.price.data = post.price

    return render_template('create_post.html', title='Update Post', form = form, legend = 'Update post')


@app.route("/post/<int:post_id>/delete",  methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('You have succesefully deleted your post!', 'success')
    return redirect(url_for('home'))

@app.route("/post/<int:post_id>/subposts", methods=['GET', 'POST'])
@login_required
def subpost(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = SubPostForm()
    if form.validate_on_submit():
        subpost = Subpost(title=form.title.data, price = form.price.data, post=post)
        db.session.add(subpost)
        db.session.commit()
        flash('You have added a new expense!', 'success')
        return redirect(url_for('home'))
    return render_template('subpost.html', title='New SubPost', form = form, legend = 'New post')

@app.route("/subpost/<int:item_id>/update",  methods=['GET', 'POST'])
@login_required
def update_subpost(item_id):
    post = Subpost.query.get_or_404(item_id)
    form = SubPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.price = form.price.data
        db.session.commit()
        flash('Your subpost has been updated!', 'success')
        return redirect(url_for('home'))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.price.data = post.price


    form.title.data = post.title
    form.price.data = post.price

    return render_template('subpost.html', title='Update Subpost', form = form, legend = 'Update post')

@app.route("/subpost/<int:post_id>/delete",  methods=['GET','POST'])
@login_required
def delete_subpost(post_id):
    post = Subpost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('You have succesefully deleted your post!', 'success')
    return redirect(url_for('home'))



@app.route("/plots/<int:post_id>")
@login_required
def plot_fig(post_id):
    
    print("Your advancement is : ")

    post = Post.query.get_or_404(post_id)
    Sposts = Subpost.query.filter(Subpost.post_id == post.id).all()

    list_price = []
    title_list = []

    for item in Sposts:
        list_price.append(item.price)
        title_list.append(item.title)
    list_price.append(post.price)
    title_list.append(post.title)
    
    plt.figure()
    plt.bar(title_list, list_price)
    plt.xlabel("Title")
    plt.ylabel("Price")

    print("plot succesefully created")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return Response(img.getvalue(), mimetype='image/png')
