from flask import Flask,render_template,request,url_for,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail,Message
import mysql.connector

with open("config.json","r") as c:
    params=json.load(c)["params"]

app=Flask(__name__)
app.secret_key="abc"

mydb=mysql.connector.connect(host="localhost",user="root",database="restaurants")

app.config['SQLALCHEMY_DATABASE_URI'] =params["uri"]
db = SQLAlchemy(app)

app.config.update(
    DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'zarvis1287@gmail.com',
	MAIL_PASSWORD = 'rj14bd1287'
	)

mail=Mail(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    password = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

class Post(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title= db.Column(db.String(80),nullable=False)
    slug= db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date= db.Column(db.String(50),nullable=False)
    img = db.Column(db.String(20), nullable=False)


@app.route("/")
def home():
    posts=Post.query.limit(3).all()
    return render_template("home.html",params=params,posts=posts)

@app.route("/register")
def register():
    return render_template("register.html",params=params)

@app.route("/adminLogin")
def adminLogin():
    return render_template("adminlogin.html",params=params)

@app.route("/bookingTable")
def bookingTable():
    return  render_template("bookingtable.html",params=params)

@app.route("/bookingHall")
def bookingHall():
    return  render_template("bookinghall.html",params=params)

@app.route("/contact")
def contact():
    return render_template("contact.html",params=params)

@app.route("/forgot")
def forgot():
    return render_template("forgot.html",params=params)

@app.route("/addUser",methods=["POST"])
def addUser():
    email=request.form.get("email")
    password=request.form.get("password")
    mycursor = mydb.cursor()
    sql = "select * from user where email='" + email + "'"
    mycursor.execute(sql)
    data = mycursor.fetchone()
    if(data is not None):
        flash("Email is already registered",'danger')
        return render_template("register.html",params=params)
    else:
        guest = User(email=email,password=password)
        db.session.add(guest)
        db.session.commit()
        msg = Message(
             'Food Fanda -Verify Your Account',
             sender='zarvis1287@gmail.com',
             recipients=[email])
        msg.html = render_template("verify.html", msg=email)
        mail.send(msg)
        flash("Verification Mail is sent to your email id","success")
        return redirect(url_for("login"))


@app.route("/verifyEmail",methods=['POST'])
def verifyEmail():
    email=request.form.get("email")
    mycursor=mydb.cursor()
    sql="update user set isverify=1 where email='"+email+"'"
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    flash("You are verified","success")
    return redirect(url_for("login"))

@app.route("/login",methods=["POST","GET"])
def login():
    if 'user' in session :
        return render_template("home.html", user=session['user'], params=params)

    if(request.method=="POST"):
        email = request.form.get("email")
        password = request.form.get("pass")
        mycursor = mydb.cursor()
        sql = "select * from user where email='" + email + "'"
        mycursor.execute(sql)
        data = mycursor.fetchone()
        mycursor.close()
        if (data is not None):
            if (data[2] == password and data[3] == 1):
                session['user'] = email
                return render_template("home.html",user=session['user'],params=params)
            elif (data[2] == password):
                msg = Message(
                    'Verify',
                    sender='zarvis1287@gmail.com',
                    recipients=
                    [email])
                msg.html = render_template("verify.html", msg=email)
                mail.send(msg)
                flash("You are not verified , please verify","danger")
                return render_template("login.html",params=params)
            else:
                flash("Password is incorrect","danger")
                return render_template("login.html", email=email,params=params)
        else:
            flash("You are not registered","danger")
            return render_template("login.html",params=params)
    else:
        return render_template("login.html",params=params)

@app.route("/recoverMail")
def recoverMail():
    email = request.args.get("email")
    msg = Message(
        'Recover Password',
        sender='zarvis1287@gmail.com',
        recipients=[email])
    msg.html = render_template("recoverPassMail.html", msg=email)
    mail.send(msg)
    flash("Reset link is sent to your registered email address","success")
    return redirect(url_for("login"))

@app.route("/resetPass",methods=["post"])
def resetPass():
    email=request.form.get("email")
    return render_template("resetPass.html",msg=email,params=params)

@app.route("/resetPass1",methods=["POST"])
def resetPass1():
    email=request.form.get("email")
    password=request.form.get("password")
    mycursor = mydb.cursor()
    sql = "update user set password='{}' where email='{}'".format(password,email)
    mycursor.execute(sql)
    mydb.commit()
    mycursor.close()
    flash("Password successfully Reset","success")
    return redirect(url_for("login"))

@app.route("/blogs/<string:post_slug>")
def post_route(post_slug):
    post=Post.query.filter_by(slug=post_slug).first()
    return render_template("blog-single.html",post=post,params=params)

@app.route("/blogs")
def blogs():
    # we can use Post.query.all() --> it will return Post object
    cursor=mydb.cursor()
    sql="select * from post limit 5"
    cursor.execute(sql)
    posts=cursor.fetchall()                             # it will return list
    cursor.close()
    return render_template("blog.html",params=params,posts=posts)

@app.route("/logout")
def logout():
    session.pop('user',None)
    return render_template("home.html",params=params)

app.run(debug=True)
