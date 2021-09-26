from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import psycopg2
import psycopg2.extras
from werkzeug.utils import secure_filename
import os

# for flask configuring
app = Flask(__name__)
app.secret_key = "erghweuigh8uh58/;["
app.permanent_session_lifetime = timedelta(days = 1)

# for our database
DB_HOST = "localhost"
DB_NAME = "bd_websitedb"
DB_USER = "postgres"
DB_PASS = "silentgee1616"

# connecting to our database
conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASS, host = DB_HOST)

@app.route("/", methods=["POST", "GET"])
def login():
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    if request.method == "POST" and "username" in request.form and "password" in request.form:
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        session["home"] = username
        session["admin"] = username
        cur.execute("BEGIN")
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cur.fetchone()
        if account:
            passwords = account["passwords"]
            usernames = account[1]
            if username == "admin" and password == passwords:
                return redirect(url_for("admin"))
            elif password == passwords:
                return redirect(url_for("home"))
            else:
                flash("Username or Password is incorrect!")
        else:
            flash("This account is not existing!")
    else:
        if "admin" in session:
            redirect(url_for("admin"))
        elif "home" in session:
            redirect(url_for("home"))
    
    return render_template("login.html")


@app.route("/home")
def home():
    if "home" in session:
        user = session["home"]
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("BEGIN")
        s = "SELECT * FROM posts"
        cur.execute(s) # execute the query
        list_post = cur.fetchall()
        return render_template("home.html", user = user, list_post = list_post)
    else:
        return redirect(url_for("login"))


@app.route("/admin")
def admin():
    if "admin" in session:
        user = session["admin"]
        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("BEGIN")
        s = "SELECT * FROM users"
        cur.execute(s) # execute the query
        list_user = cur.fetchall()
        p = "SELECT * FROM posts"
        cur.execute(p) # execute the query
        list_post = cur.fetchall()
        admin_id = "SELECT user_id FROM users WHERE user_id = 2"
        cur.execute(admin_id)
        list_id = cur.fetchall()
        ad_id = list_id[0][0]

        return render_template("admin.html", user = user, list_user = list_user, list_post = list_post, ad_id = ad_id)
    else:
        return redirect(url_for("login"))


# FOR UPDATE USER
@app.route('/edit/<user_id>', methods=["POST", "GET"])
def get_user(user_id):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # for editing users
    cur.execute("BEGIN")
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id))
    data = cur.fetchall()
    cur.close()
    return render_template("edit.html", user = data[0])


@app.route('/update/<user_id>', methods=['POST'])
def update_user(user_id):
    if request.method == 'POST':
        username = request.form["username"]
        passwords = request.form["password"]

        cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        cur.execute("BEGIN")
        cur.execute("""UPDATE users SET username = %s, passwords = %s WHERE user_id = %s""", (username, passwords, user_id))
        conn.commit()
        return redirect(url_for('admin'))


# FOR ADDING POST
@app.route("/add/<user_id>", methods=["POST", "GET"])
def add(user_id):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # for editing users
    cur.execute("BEGIN")
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id))
    data = cur.fetchall()
    cur.close()

    return render_template("add_post.html", user = data[0])


UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/added/<user_id>', methods=['POST'])
def added_post(user_id):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            messages = request.form["message"]
            cur.execute("BEGIN")
            cur.execute("INSERT INTO posts (picture, messages, user_id) VALUES (%s, %s, %s)", (filename, messages, user_id))
            conn.commit()

            return redirect(url_for('admin'))
        else:
            return redirect(request.url)
        
    return redirect(url_for('admin'))


# FOR UPDATE POST
@app.route("/edit_post/<post_id>", methods=["POST", "GET"])
def edit_post(post_id):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    # for editing users
    cur.execute("BEGIN")
    cur.execute("SELECT * FROM posts WHERE post_id = %s", (post_id))
    data = cur.fetchall()
    cur.close()

    return render_template("edit_post.html", post = data[0])


@app.route('/update_post/<post_id>', methods=['POST'])
def update_post(post_id):

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            messages = request.form["message"]
            cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
            cur.execute("BEGIN")
            cur.execute("""UPDATE posts SET picture = %s, messages = %s WHERE post_id = %s""", (filename, messages, post_id))
            conn.commit()

            return redirect(url_for('admin'))
        else:
            return redirect(request.url)
        
    return redirect(url_for('admin'))


# FOR DELETING POSTS
@app.route("/delete_post/<string:post_id>", methods=["POST", "GET"])
def delete_post(post_id):
    cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    cur.execute("BEGIN")
    cur.execute("DELETE FROM posts WHERE post_id = {0}".format(post_id))
    conn.commit()
    return redirect(url_for('admin'))


# FOR GALLERY PAGE
@app.route("/gallery")
def gallery():
    return render_template("gallery.html")
    

@app.route("/logout")
def logout():
    session.pop("home", None)
    session.pop("admin", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug = True)