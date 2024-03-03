from flask import Flask,redirect,render_template,request,url_for,flash,session
import sqlite3
from functools import wraps
from flask_login import current_user
import datetime


# Establish a connection to the database

con = sqlite3.connect('blog.db')

# Create a cursor object to execute SQL commands

cur = con.cursor()

# Execute the SQL command to create the 'user' table
cur.execute('''CREATE TABLE IF NOT EXISTS user (
                userid INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(25) NOT NULL,
                email VARCHAR(30) UNIQUE,
                password VARCHAR(10) NOT NULL
            )''')


# Commit the changes to the database
con.commit()
cur.execute('''CREATE TABLE IF NOT EXISTS blogdata (
                blogid INTEGER PRIMARY KEY AUTOINCREMENT,
                authorname VARCHAR(25) NOT NULL,
                title VARCHAR(50) NOT NULL,
                content VARCHAR(500) NOT NULL,
                dataposted varchar(15)
            )''')
con.commit()
# Close the connection
con.close()






app = Flask(__name__)
app.secret_key = 'your_secret_key'




posts = [
    {
        'id':1,
        'author': 'John Doe',
        'title': 'Introduction to Python Programming',
        'content': 'Python is a high-level programming language...',
        'date_posted': '2024-02-26'
    },
    {
        'id':2,
        'author': 'Jane Smith',
        'title': 'Machine Learning Basics',
        'content': 'Machine learning is a subset of artificial intelligence...',
        'date_posted': '2024-02-25'
    },
    {
        'id':3,
        'author': 'Alex Johnson',
        'title': 'Web Development with Flask',
        'content': 'Flask is a lightweight WSGI web application framework...',
        'date_posted': '2024-02-24'
    },
    {
        'id':4,
        'author': 'Emily Brown',
        'title': 'Data Analysis with Pandas',
        'content': 'Pandas is an open-source data analysis and manipulation library...',
        'date_posted': '2024-02-23'
    },
    {
        'id':5,
        'author': 'Michael Lee',
        'title': 'Introduction to Natural Language Processing',
        'content': 'Natural Language Processing (NLP) is a field of artificial intelligence...',
        'date_posted': '2024-02-22'
    }
]




# Function decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to login first", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function








def authenticate(email,password):
    con = sqlite3.Connection('blog.db')
    cur = con.cursor()
    cur.execute('''select * from user where email = ? and password = ? 
                ''',(email,password))
    user = cur.fetchone()
    con.close()
    return user

@app.route('/')
@app.route('/home')
@login_required
def home():
    con = sqlite3.Connection('blog.db')
    cur = con.cursor()
    cur.execute('select * from blogdata')
    posts = cur.fetchall()
    posts.reverse()
    username = None
    if 'username' in session:
        username = session['username']
        # if username==posts[1]:
        #     editdelete = True
    return render_template("home.html",posts = posts, log='user_id' in session,username=username)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    #flash("You have been logged out", "info")
    return redirect(url_for('home'))


@app.route('/about')
@login_required
def about():
    return render_template("about.html",title = "About",log='user_id' in session)

@app.route('/register',methods = ['POST','GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect('blog.db')
        cur = con.cursor()
        cur.execute(''' insert into user (username,email,password) values (?,?,?)
                    ''',(username,email,password,))
        con.commit()
        #flash('Registration successful! Please log in.')  # Flash a success message
        return redirect('/login') 
            
    return render_template("register.html",title = "Register")

@app.route('/login',methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = authenticate(email=email,password=password)
        if user:
            #flash("Login successfully")
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            flash("invalid email or password")
    # Pass 'log' variable to indicate if the user is logged in or not
    if 'user_id' in session:
        log = True  # User is logged in
    else:
        log = False  # User is not logged in        
        
    return render_template("login.html",title = "Login",log=log)

@app.route('/content',methods = ['POST','GET'])
@login_required
def content():
    if request.method == 'POST':
        blogtitle = request.form['blogtitle']
        blogcontent = request.form['blogcontent']
        # id = len(posts)+1
        blogdateposted = datetime.date.today()
        if 'username' in session:
            username = session['username']
            author = username
            con = sqlite3.Connection('blog.db')
            cur = con.cursor()
            cur.execute("insert into blogdata (authorname,title,content,dataposted) values (?,?,?,?)",(author,blogtitle,blogcontent,blogdateposted))
            con.commit()
            con.close()
            #flash('successfully submitted your blog')
            return redirect('/home')
        else:
            flash('not submitted')
            return redirect('/content')      
    return render_template("content.html",title = "content",log='user_id' in session)

@app.route('/edit/<int:id>',methods = ['GET','POST'])
@login_required
def edit(id):
    con = sqlite3.Connection('blog.db')
    cur = con.cursor()
    cur.execute('select * from blogdata where blogid = ?',(id,))
    postsdata = cur.fetchone()
    print(postsdata[3])
    if request.method == 'POST':
        blogtitle = request.form['blogtitle'] 
        blogcontent = request.form['blogcontent']
        # id = len(posts)+1
        blogdateposted = datetime.date.today()
        if 'username' in session:
            con = sqlite3.Connection('blog.db')
            cur = con.cursor()
            cur.execute("update blogdata set title = ?,content=?,dataposted=? where blogid = ?",(blogtitle,blogcontent,blogdateposted,id))
            con.commit()
            con.close()
            #flash('successfully edited your blog')
            return redirect('/home')
        else:
            flash('not edited')
            return redirect('/edit')      
    return render_template("edit.html",title = "edit",log='user_id' in session,blogtitle=postsdata[2],blogcontent=postsdata[3])

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'username' in session:
        con = sqlite3.Connection('blog.db')
        cur = con.cursor()
        cur.execute("delete from blogdata where blogid = ?",(id,))
        con.commit()
        con.close()
        #flash('successfully deleted your blog')
        return redirect('/home')
    else:
        flash('not deleted')
        return redirect('/delete')      
    # return render_template("edit.html",title = "edit",log='user_id' in session)
    

@app.route('/detail/<int:id>')
@login_required
def detail(id):
    con = sqlite3.Connection('blog.db')
    cur = con.cursor()
    cur.execute("select * from blogdata where blogid = ?",(id,))
    posted = cur.fetchone()
    con.close()
    post = list(posted)
    if post:
        return render_template("detail.html", title="Detail", log='user_id' in session, blogtitle=post[2], content=post[3])
    else:
        # flash("Post not found", "warning")
        return redirect(url_for('home'))


    

if __name__ == "__main__":
  app.run(host = '0.0.0.0', port=8080 ,debug=True )