from flask import Blueprint, render_template, request, redirect, flash, url_for, session, wrappers
from dbfunc import getConnection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps 

auth = Blueprint("auth",__name__)

#sign up endpoint
@auth.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name").strip()
        last_name = request.form.get("last_name").strip()
        username = request.form.get("username").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # make sure user can sign up after filling all inputs
        if not first_name or not last_name or not username or not email or not password:
            flash("All fields are required.")
            return render_template("signup.html")
        
        #hash password
        password_hash = generate_password_hash(password)

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
        
        cursor = None
        try: 
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (first_name, last_name, username, email, password_hash) VALUES (%s, %s, %s, %s, %s)",
                        (first_name, last_name, username, email, password_hash))
            conn.commit() 
            flash("Signup successful. Please log in.")
            return redirect(url_for("auth.login"))
        except Exception:
            return "Signup failed"
        finally:
            if cursor:
                cursor.close()
            conn.close()
        
    
    return render_template("signup.html")

#login endpoint
@auth.route("/login", methods = ["POST", "GET"])
def login():

    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password", "")
            

        if not username or not password:
            flash("Username or Password missing")
            return render_template("login.html")
                

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
                
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, password_hash
                FROM users 
                WHERE username = %s
            """, (username,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user[2], password):
                flash("Invalid username or password.")
                return render_template("login.html")

            # save logged-in user in session
            session["user_id"] = user[0]
            session["username"] = user[1]

            flash("Login Successful")
            return redirect(url_for("profile"))

        except Exception:
                return "Login failed", 500

        finally:
            if cursor:
                cursor.close()
            conn.close()
   
    return render_template("login.html")


#logout endpoint
@auth.route("/logout")
# @login_required
def logout():
    session.clear()
    flash("User successfully logged out")
    return redirect(url_for("auth.login"))


# wrapper to secure endpoint
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:            
            flash("Please log in to access page.")
            return redirect(url_for("auth.login"))   
    return wrap


@auth.route("/profile/password", methods=["GET", "POST"])
@login_required
def update_password():
    user_id = session.get("user_id")
    
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
            

        if not current_password or not new_password or not confirm_password:
            flash("All password fields required.")
            return redirect(request.url)
                
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(request.url)

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
                
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT password_hash
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user[0], current_password):
                flash("Current password is incorrect.")
                return redirect(request.url)
            
            new_hash = generate_password_hash(new_password)

            cursor.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
            """, (new_hash, user_id))

            conn.commit()
            flash("Password have been updated")
            return redirect(url_for("profile"))

        except Exception:
                return "Faild to updte password", 500

        finally:
            if cursor:
                cursor.close()
            conn.close()
   
    return render_template("update_password.html")


