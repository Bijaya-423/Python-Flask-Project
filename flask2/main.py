from flask import Flask, render_template, request ,  flash, redirect, url_for, session
# from flask_mail import Mail
# from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os
import math
import json

# import pymysql
# pymysql.install_as_MySQLdb()


with open('config.json', 'r') as c:
    params = json.load(c) ["params"]
    
local_server = True
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = params['upload_location']

'''app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password'])
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  
# app.config['MAIL_PASSWORD'] = 'your-app-password' 

mail = Mail(app)'''


app.secret_key = 'super-secret-key' # Required for flash messages

# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:@localhost/codingthunder'
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://root:@localhost/codingthunder'

local_server = True
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=True)
    mes = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    # posts = Posts.query.filter_by().all()[0:params['no_of_posts']]#show only 5 blog
    # return render_template('index.html', params= params, posts=posts)
    return render_template('index.html', params= params)

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content =  request.form.get('content')  
            img_file =  request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Posts(title=box_title, slug=slug, content=content, tagline=tline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = contact
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                # db.session.add(post)
                db.session.commit()
                return redirect('/edit/'+sno)
            
        post = Posts.query.filter_by(sno=sno).first()        
        return render_template('edit.html', params=params, post=post)
            
@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully"
            
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

            
@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


    
@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        if not name or not message or not email:
            return "Name, Message, and Email are required!", 400
                
        entry = Contacts(name=name, phone_num=phone, mes=message, email=email, date=datetime.now())
        db.session.add(entry)
        db.session.commit() 
        # mail.send_message(subject='New Message From ' + name, sender=email, recipients = [params['gmail-user']], body = "message"+ "\n" + phone)
        
 
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html' , success = "Contact information submitted Successfully", params= params)

@app.route("/about")
def about():
    # print("Params debug:", params)
    return render_template('about.html', params= params)

@app.route("/blog")
def blog():
    posts = Posts.query.filter_by().all()
    #[0:params['no_of_posts']]#show only 5 blog
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    
    # posts = Posts.query.all()  # Get all posts
    # num_of_posts = int(params['no_of_posts'])
    # total_posts = len(posts)
    # last = math.ceil(total_posts / num_of_posts) - 1

    # page = request.args.get('page', 1, type=int)
    # start = (page - 1) * num_of_posts
    # end = start + num_of_posts
    # posts = posts[start:end]
    
    #Pagination logic
    #first
    if (page == 1):
        prev = '#'
        next = "/blog?page=" + str(page + 1)
    #last
    elif (page == last):
        prev = "/blog?page=" + str(page - 1)
        next = '#'
        # prev = page - 1
        # next = #
    #middle
    else:
        prev = "/blog?page=" + str(page - 1)
        next = "/blog?page=" + str(page + 1)
        # prev = page - 1
        # next = page + 1
    return render_template('blog.html', params= params, posts=posts, prev=prev, next=next)

@app.route("/dashboard" , methods=['GET','POST'])
def dashboard():
    
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts = posts)
    
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params= params, posts = posts)
            
    return render_template('login.html', params= params)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)



@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    print(post)
    # if not post:
    #     return "Post not found", 404
    return render_template('post.html', params= params, post = post)


if __name__ == "__main__":
    app.run(debug=True)