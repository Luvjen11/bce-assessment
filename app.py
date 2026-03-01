from flask import Flask, render_template
from dotenv import load_dotenv
load_dotenv()
import os
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

from auth import auth
from error import error_page
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(error_page)

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/event")
def event():
    return render_template("event.html")

@app.route("/event1")
def event1():
    return render_template("event1.html")

@app.route("/event2")
def event2():
    return render_template("event2.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug = True)
