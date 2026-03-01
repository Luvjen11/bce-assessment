from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from dbfunc import getConnection
from werkzeug.security import generate_password_hash, check_password_hash

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
            cursor.execute("SELECT user_id, username, password_hash FROM users WHERE username = %s",
                        (username,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user[2], password):
                flash("Invalid username or password.")
                return render_template("login.html")

            # save logged-in user in session
            session["user_id"] = user[0]
            session["username"] = user[1]

            # TODO: search for how to redirect user to the page they were in
            return redirect(url_for("profile"))

        except Exception:
            return "Login failed"
        finally:
            if cursor:
                cursor.close()
            conn.close()
        
    
    return render_template("login.html")

#logout endpoint
@auth.route("/logout")
def logout():
    session.clear()
    flash("User successfully logged out")
    return redirect(url_for("auth.login"))

