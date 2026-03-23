from flask import Flask, render_template, request, abort, redirect, flash, url_for, session
from datetime import datetime, date 
from dbfunc import getConnection
from dotenv import load_dotenv
load_dotenv()
import os
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

from auth import auth, login_required
from error import error_page
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(error_page)

# functions 

# fetch all events
def get_all_events_with_venue():

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return None
        
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
                e.image_filename,
                e.is_free,
                v.name AS venue_name,
                v.address AS venue_address,
                GROUP_CONCAT(c.name ORDER BY c.name SEPARATOR ",") AS categories 
            FROM events e 
            LEFT JOIN venues v ON e.venue_id = v.venue_id 
            LEFT JOIN event_categories ec ON e.event_id = ec.event_id
            LEFT JOIN categories c ON ec.category_id = c.category_id
            GROUP BY
                e.event_id, e.name, e.start_date, e.end_date, e.price, e.last_date_booking,
                e.description, e.venue_id, e.image_filename, e.is_free,
                v.name, v.address
            ORDER BY e.start_date ASC 
            """)
            events = cursor.fetchall()
            return events
        
        except Exception as e:
            print(f"Failed to fetch event details: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            conn.close()

# fetch one single event
def get_event_with_venue(event_id):
        conn = getConnection()
        if conn is None or not conn.is_connected():
            return None
        
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
                e.image_filename,
                e.is_free,
                e.special_conditions,
                v.name AS venue_name,
                v.address AS venue_address,
                v.capacity
            FROM events e 
            LEFT JOIN venues v ON e.venue_id = v.venue_id 
            WHERE e.event_id = %s 
            """, (event_id,))
            event = cursor.fetchone()
            return event
            
        except Exception as e:
            print(f"Failed to fetch event details: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            conn.close()

# get tickets booked for event 
def get_tickets_booked_for_event(event_id):
    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
    
    cursor = None
    try: 
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT COALESCE(SUM(bi.quantity), 0)
        AS tickets_booked
        FROM bookings b
        JOIN booking_items bi ON b.booking_id = bi.booking_id
        WHERE b.event_id = %s 
        AND b.status = "confirmed"               
        """, (event_id,))
        booked_tickets = cursor.fetchone()

        return booked_tickets["tickets_booked"] if booked_tickets else 0          
    
    except Exception as e:
        print(f"Error fetching booked tickets: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()
        conn.close()


        
# endpoints 
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    events = get_all_events_with_venue()
    today = date.today()

    upcoming_events = [e for e in events if e.get("start_date") and e["start_date"].date() >= today]
    past_events = [e for e in events if e.get("start_date") and e["start_date"].date() < today]

    return render_template("index.html", events=events, upcoming_events=upcoming_events,
        past_events=past_events)

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

# fetch one single event endpoint
@app.route("/event/<int:event_id>", methods=["GET"])
def event_with_venue(event_id):
    event = get_event_with_venue(event_id)
    if event is None:
        return render_template("404.html"), 404

    return render_template("event.html", event=event)

# book an event
@app.route("/event/<int:event_id>/book", methods=["GET", "POST"])
def book_event(event_id):

    # fetch event with venue
    event = get_event_with_venue(event_id)

    # if no event return 404
    if not event:
        return render_template("404.html"), 404
        
    # get booked tickets
    booked_tickets = get_tickets_booked_for_event(event_id)

    # get remaining tickets
    remaining_tickets = event.get("capacity") - booked_tickets
    
    # return booking page
    if request.method == "GET":
        return render_template("booking.html", event=event, remaining_tickets= remaining_tickets)

    # read form
    if request.method == "POST":

        quantity_raw = request.form.get("quantity")
        student_discount = request.form.get("student_discount") == "1"
        terms = request.form.get("terms") == "1"
        event_day = request.form.get("event_day")

    # validate quantity
    try: 
        quantity = int(quantity_raw)
        if quantity < 1:
                raise ValueError
    except (TypeError, ValueError):
        flash("Please enter a valid ticket quantity.")
        return redirect(request.url)
    
    # validate terms
    if not terms:
        flash("You must accept the terms and conditions.")
        return redirect(request.url)
    
    # check if user is logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to book this event")
        return redirect(url_for("auth.login"))
    
    # validate booking deadline
    if datetime.now() > event["last_date_booking"]:
        flash("Booking for this event is closed.")
        return redirect(url_for("event_with_venue", event_id=event_id))

    # validate capacity
    if remaining_tickets <= 0:
        flash("This event is fully booked.")
        return redirect(url_for("event_with_venue", event_id=event_id))
    
    if quantity > remaining_tickets:
        flash(f"Only {remaining_tickets} tickets are available for this event.")
        return redirect(request.url)
    
    # calculate price
    unit_price = 0 if event.get("is_free") else float(event.get("price") or 0)
    total_price = unit_price * quantity
    if student_discount:
        total_price = round(total_price * 0.9, 2)

    # insert into bookings
    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
        
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO bookings (user_id, event_id, booking_date, status, total_price) VALUES (%s, %s, %s, %s, %s)
                       """, (user_id, event_id, datetime.now(), "confirmed", total_price))
        
        booking_id = cursor.lastrowid

        booking_event_day = event_day if event_day else event.get("start_date")

        # insert into booking_item
        cursor.execute("""INSERT INTO booking_items (booking_id, event_day, quantity, unit_price) VALUES (%s, %s, %s, %s)
                       """, (booking_id, booking_event_day, quantity, unit_price))
        
        conn.commit() 

        flash("Booking successful.")
        return redirect(url_for("booking_receipt", booking_id = booking_id))
    except Exception as e:
            conn.rollback()
            print(f"Booking failed: {e}")
            return "Failed to create booking", 500
    finally:
            if cursor:
                cursor.close()
            conn.close()
    
# reciept page
@app.route("/booking/<int:booking_id>/receipt", methods=["GET"])
def booking_receipt(booking_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login to view your receipt.")
        return redirect(url_for("auth.login"))
    
    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                b.booking_id,
                b.booking_date,
                b.status,
                b.total_price,
                e.name AS event_name,
                e.start_date,
                e.end_date,
                v.name AS venue_name,
                v.address AS venue_address
            FROM bookings b
            JOIN events e ON b.event_id = e.event_id
            LEFT JOIN venues v ON e.venue_id = v.venue_id
            WHERE b.booking_id = %s AND b.user_id = %s
        """, (booking_id, user_id))
        
        booking = cursor.fetchone()

        if booking is None:
            return render_template("404.html"), 404
        
        cursor.execute("""
            SELECT
                event_day,
                quantity,
                unit_price
            FROM booking_items
            WHERE booking_id = %s
        """, (booking_id, ))
        items = cursor.fetchall()

        return render_template("booking_reciept.html", booking=booking, items=items)
    except:
        return "Failed to load receipt", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# @app.route("/getcookie")
# def get_cookie():
#     name = request.cookies.get("userID")
#     return "<h1>Welcome" + name + "<h1>"

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