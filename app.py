from flask import Flask, render_template, request, abort
from dbfunc import getConnection
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
    events = get_all_events_with_venue()
    return render_template("index.html", events=events)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/events")
def events():
    events = get_all_events_with_venue()
    return render_template("events.html", events=events)

# fetch all events
def get_all_events_with_venue():

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
        
        cursor = None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
            SELECT 
                e.event_id, 
                e.name,
                e.start_date,
                e.end_date,
                e.price,
                e.last_date_booking,
                e.description,
                e.venue_id,
                v.name AS venue_name,
                v.address AS venue_address 
            FROM events e 
            LEFT JOIN venues v ON e.venue_id = v.venue_id 
            ORDER BY e.start_date ASC 
            """)
            events = cursor.fetchall()
            return events
        except:
            return "Failed to fetch events", 500
        finally:
            if cursor:
                cursor.close()
            conn.close()


# fetch one single event
@app.route("/event/<int:event_id>", methods=["GET"])
def get_event_with_venue(event_id):
    if request.method == "GET":

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
        
        cursor = None
        try: 
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
            SELECT 
                e.event_id, 
                e.name,
                e.start_date,
                e.end_date,
                e.price,
                e.last_date_booking,
                e.description,
                e.venue_id,
                v.name AS venue_name,
                v.address AS venue_address 
            FROM events e 
            LEFT JOIN venues v ON e.venue_id = v.venue_id 
            WHERE e.event_id = %s 
            """, (event_id,))
            event = cursor.fetchone()

            if event is None:
                return render_template("404.html"), 404
            
        except Exception:
            return "Failed to fetch event details", 500
        finally:
            if cursor:
                cursor.close()
            conn.close()
    return render_template("event.html", event=event)

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


# if request.method == "GET":

#         conn = getConnection()
#         if conn is None or not conn.is_connected():
#             return "DB Connection Error", 500
        
#         cursor = None

#         try:
#             cursor = conn.cursor(dictionary=True)
#             cursor.execute()
#         except:
#             return "Failed to fetch event details", 500
#         finally:
#             if cursor:
#                 cursor.close()
#             conn.close()