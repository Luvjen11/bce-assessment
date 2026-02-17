from flask import Flask, render_template
app = Flask(__name__)

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")


if __name__ == "__main__":
    app.run(debug = True)

# error
@app.errorhandler(404)
def not_found_error(error):
    return render_template(), 404