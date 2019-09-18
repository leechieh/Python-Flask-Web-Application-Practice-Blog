from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required 
from blog import db
from blog.models import User, BlogPost
from blog.users.forms import RegistrationForm, LoginForm, UpdateUserForm
from blog.users.pic_handler import add_profile_pic
import os


users = Blueprint('users', __name__)

# Register user
@users.route("/register", methods = ['GET','POST'])
def register():
	form = RegistrationForm()

	if form.validate_on_submit():
		user = User(email=form.email.data, 
			        username=form.username.data,
			        password=form.password.data)
		db.session.add(user)
		db.session.commit()
		
		return redirect(url_for('users.login'))
	return render_template('register.html', form=form)

# Login user
@users.route("/login", methods = ['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():

		user = User.query.filter_by(email=form.email.data).first()

		if user is not None:
			if user.check_password(form.password.data):
				login_user(user)

				next = request.args.get('next')

				if next== None or not next[0] == '/':
					next = url_for('core.index')
				return redirect(next)
	return render_template('login.html', form=form)

# Logout user
@users.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('core.index'))

# Account
@users.route("/account",methods=['GET','POST'])
@login_required
def account():

	form = UpdateUserForm()

	if form.validate_on_submit():
		if form.picture.data:
			username = current_user.username
			pic = add_profile_pic(form.picture.data,username)
			current_user.profile_image = pic

		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		return redirect(url_for('users.account'))

	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email

	profile_image = url_for('static',filename='profile_pics/'+current_user.profile_image)
	return render_template('account.html', profile_image=profile_image, form = form )

# User's List of Blog posts 
@users.route('/user/<username>')
def user_posts(username):
	page = request.args.get('page',1,type=int)	
	user = User.query.filter_by(username=username).first_or_404()
	blog_posts = BlogPost.query.filter_by(author = user).order_by(BlogPost.date.desc()).paginate(page=page,per_page=5)
	return render_template('user_blog_posts.html', blog_posts=blog_posts, user=user)

# Remove user account (only the user can remove his/her own account). Posts posted by the user will also be removed
@users.route('/delete_account', methods=['GET','POST'])
@login_required
def delete_account():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	posts = BlogPost.query.filter_by(author = user)

	for post in posts:
		db.session.delete(post)
	db.session.delete(user)
	db.session.commit()

	return redirect(url_for('core.index'))



