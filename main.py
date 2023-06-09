from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import math
from sendMail import sendmail

# Define app
with open('config.json', 'r') as c: 
    params = json.load(c)["params"]

local_Server = params['local_server']
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.secret_key = 'super-secret-key'

if(local_Server) :
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else :
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard() : 
    if 'user' in session and session['user'] == params['admin_user'] :
        posts = Posts.query.all() 
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST' :
        # Redirect to admin panel 
        username = request.form.get('uname') 
        userpass = request.form.get('pass')
        if(username == params['admin_user'] and userpass == params['admin_password']) :
            # set the session variable
            session['user'] = username
            posts = Posts.query.all()

            return render_template('dashboard.html', params=params, posts=posts)
    else :
        posts = Posts.query.all()
        return render_template('login.html', params=params, posts=posts)

@app.route("/")
def home() :
    posts = Posts.query.filter_by().all()
    last = math.ceil((len(posts)/int(params['no_of_posts'])))
    #[0:params['no_of_posts']]
    pageno = request.args.get('page')
    if(not str(pageno).isnumeric()) : 
        pageno = 1
    
    pageno = int(pageno)
    # Post slicing done here 
    posts = posts[(pageno-1)*int(params['no_of_posts']) : (pageno-1)*int(params['no_of_posts']) + int(params['no_of_posts']) ]

    # Pagination Logic 
    # First Page ( prev=#, next=page+1 )
    # Middle Page ( prev=page-1, next=page+1 )
    # Last Page ( prev=page-1, next=# )
    if(pageno == 1):
        prev = "#"
        next = "/?page="+ str(pageno+1)
    elif (pageno == last) :
        prev = "/?page="+ str(pageno-1)
        next = "#"
    else :
        prev = "/?page="+ str(pageno-1)
        next = "/?page="+ str(pageno+1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)

@app.route("/about")
def about() :
    return render_template('about.html', params=params)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), unique=True,nullable=False)

@app.route("/contact", methods = ['GET','POST'])
def contact() :
    if(request.method == 'POST') :
        ''' Add entry to the database '''  
        '''Fetch data and add it to the database''' 
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone_no')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, message=message, date=datetime.now(), email=email)

        db.session.add(entry)
        db.session.commit()

        sendmail(name, phone, email, message)

    return render_template('contact.html', params=params)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    admin = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(25), nullable=False)
    date = db.Column(db.String(12), nullable=True)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug) :
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/edit/<string:sno>", methods = ['GET','POST'])
def edit(sno) :
    if 'user' in session and session['user'] == params['admin_user'] :
        if request.method == 'POST':
            box_title = request.form.get('title')
            admin = request.form.get('admin')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            # sno == '0' means that add a new post
            if (sno == '0'):
                post = Posts(title=box_title, admin=admin, slug=slug, content=content, tagline=tagline, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit() 
            # otherwise edit existing post
            else :
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.admin = admin
                post.tline = tagline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()

            return redirect('/dashboard')

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)

@app.route("/uploader", methods = ['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user'] :
        if (request.method == 'POST') :
            f = request.files['file1']
            f.save( os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded Successfully !!"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user'] :
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
