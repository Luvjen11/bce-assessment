from flask import Blueprint, render_template, request, redirect, flash, url_for, session, wrappers
from dbfunc import getConnection
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps  

admin = Blueprint("admin",__name__)

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in as admin to access page.")
            return redirect(url_for("admin.admin_login"))   
        
        if session.get("role") != "admin":
            flash("You need to be admin.")
            return redirect(url_for("index"))  

        return f(*args, **kwargs) 
    return wrapper

#login endpoint
@admin.route("/login", methods = ["POST", "GET"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Username or Password missing")
            return render_template("admin_login.html")         

        conn = getConnection()
        if conn is None or not conn.is_connected():
            return "DB Connection Error", 500
                
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, username, password_hash, role
                FROM users 
                WHERE username = %s
            """, (username,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user[2], password):
                flash("Invalid username or password.")
                return render_template("admin_login.html")

            if user[3] != "admin":
                flash("You need admin access.")
                return redirect(url_for("admin.admin_login"))

            # save logged-in user in session
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role"] = user[3]

            flash("Login Successful")
            return redirect(url_for("admin.admin_dashboard"))

        except Exception:
                return "Login failed", 500
        finally:
            if cursor:
                cursor.close()
            conn.close()
   
    return render_template("admin_login.html")

@admin.route("/dashboard")
@admin_required
def admin_dashboard():

    edit_event_id = request.args.get("edit_event_id", type=int)
    edit_venue_id = request.args.get("edit_venue_id", type=int)

    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("""
            SELECT
                e.event_id,
                e.name,
                e.start_date,
                e.end_date,
                e.price,
                e.last_date_booking,
                e.description,
                e.image_filename,
                e.special_conditions,  
                e.venue_id,
                v.name AS venue_name
            FROM events e
            LEFT JOIN venues v ON e.venue_id = v.venue_id
            ORDER BY e.start_date ASC 
        """)
        events = cursor.fetchall()

        # venues
        cursor.execute("""
            SELECT venue_id, name, capacity, address, suitable_event_types
            FROM venues
            ORDER BY name ASC
        """)

        venues = cursor.fetchall()

        # edit event
        edit_event = None
        if edit_event_id:
            cursor.execute("""
                SELECT
                    event_id,
                    name,
                    start_date,
                    end_date,
                    price,
                    last_date_booking,
                    description,
                    image_filename,
                    special_conditions,
                    venue_id
                FROM events
                WHERE event_id = %s
            """, (edit_event_id,))
        
        edit_event = cursor.fetchone()

        # edit venue
        edit_venue = None
        if edit_venue_id:
            cursor.execute("""
                SELECT venue_id, name, capacity, address, suitable_event_types
                FROM venues
                WHERE venue_id = %s
            """, (edit_venue_id,))

        edit_venue = cursor.fetchone()
        
        return render_template("admin_dashboard.html", events=events, venues=venues, edit_venue=edit_venue, edit_event=edit_event)
    
    except Exception:
        return "Admin dashboard failed", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

#logout endpoint
@admin.route("/logout")
def logout():
    session.clear()
    flash("Admin successfully logged out")
    return redirect(url_for("admin.admin_login"))


@admin.route("/events/add", methods=["GET", "POST"]) 
@admin_required
def add_events():

    if request.method == "GET":
        return redirect(url_for("admin.admin_dashboard"))

    name = request.form.get("name", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    price = request.form.get("price", "").strip()
    last_date_booking = request.form.get("last_date_booking", "").strip()
    description = request.form.get("description", "").strip()
    special_conditions = request.form.get("special_conditions", "").strip()
    image_filename = request.form.get("image_filename", "").strip()
    venue_id = request.form.get("venue_id", "").strip()

    if not name or not start_date or not end_date or not price or not last_date_booking or not venue_id:
            flash("Please fill in all required fields")
            return redirect(url_for("admin.admin_dashboard"))


    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("""
            INSERT INTO events (
                name,
                start_date,
                end_date,
                price,
                last_date_booking,
                description,
                image_filename,
                special_conditions,  
                venue_id
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, start_date, end_date, price, last_date_booking, description, image_filename, special_conditions, venue_id),)
        conn.commit()
        flash("Event added successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Add event error: {e}")
        return "Failed to add event", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

@admin.route("/events/<int:event_id>/edit", methods=["GET", "POST"]) 
@admin_required
def edit_events(event_id):

    if request.method == "GET":
        return redirect(url_for("admin.admin_dashboard", edit_event_id=event_id))

    name = request.form.get("name", "").strip()
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip()
    price = request.form.get("price", "").strip()
    last_date_booking = request.form.get("last_date_booking", "").strip()
    description = request.form.get("description", "").strip()
    special_conditions = request.form.get("special_conditions", "").strip()
    image_filename = request.form.get("image_filename", "").strip()
    venue_id = request.form.get("venue_id", "").strip()

    if not name or not start_date or not end_date or not price or not last_date_booking or not venue_id:
            flash("Please fill in all required fields")
            return redirect(url_for("admin.admin_dashboard"))


    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("""
            UPDATE events
            SET
                name = %s,
                start_date = %s,
                end_date = %s,
                price = %s,
                last_date_booking = %s,
                description = %s,
                image_filename = %s,
                special_conditions = %s,  
                venue_id = %s
            WHERE event_id = %s
        """, (name, start_date, end_date, price, last_date_booking, description, image_filename, special_conditions, venue_id, event_id),)
        conn.commit()
        flash("Event updated successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Update event error: {e}")
        return "Failed to update event", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

@admin.route("/events/<int:event_id>/delete", methods=[ "POST"]) 
@admin_required
def delete_events(event_id):

    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("SELECT COUNT(*) AS booking_count FROM bookings WHERE event_id = %s", (event_id,))
        result = cursor.fetchone()

        if result["booking_count"] > 0:
            flash("Cannot delete event that already has bookings.")
            return redirect(url_for("admin.admin_dashboard"))
        
        delete_cursor = conn.cursor()
        delete_cursor.execute("DELETE FROM event_categories WHERE event_id = %s", (event_id,))
        delete_cursor.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
        conn.commit()
        delete_cursor.close()
        flash("Event deleted successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Delete event error: {e}")
        return "Failed to delete event", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()


# venue management
@admin.route("/venues/add", methods=["GET", "POST"]) 
@admin_required
def add_venues():

    if request.method == "GET":
        return redirect(url_for("admin.admin_dashboard"))

    name = request.form.get("name", "").strip()
    capacity = request.form.get("capacity", "").strip()
    address = request.form.get("address", "").strip()
    suitable_event_types = request.form.get("suitable_event_types", "").strip()

    if not name or not capacity or not address:
            flash("Please fill in all required fields")
            return redirect(url_for("admin.admin_dashboard"))


    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("""
            INSERT INTO venues (
                name,
                capacity,
                address,
                suitable_event_types
            ) 
            VALUES (%s, %s, %s, %s)
        """, (name, capacity, address, suitable_event_types),)
        conn.commit()
        flash("Venue added successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Add venue error: {e}")
        return "Failed to add venue", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

@admin.route("/venues/<int:venue_id>/edit", methods=["GET", "POST"]) 
@admin_required
def edit_venues(venue_id):

    if request.method == "GET":
        return redirect(url_for("admin.admin_dashboard", edit_venue_id=venue_id))

    name = request.form.get("name", "").strip()
    capacity = request.form.get("capacity", "").strip()
    address = request.form.get("address", "").strip()
    suitable_event_types = request.form.get("suitable_event_types", "").strip()


    if not name or not capacity or not address:
            flash("Please fill in all required fields")
            return redirect(url_for("admin.admin_dashboard", edit_venue_id=venue_id))


    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all venues
        cursor.execute("""
            UPDATE venues
            SET
                name = %s,
                capacity = %s,
                address = %s,
                suitable_event_types = %s
            WHERE venue_id = %s
        """, (name, capacity, address, suitable_event_types, venue_id),)
        conn.commit()
        flash("Venue updated successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Update venue error: {e}")
        return "Failed to update venue", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()

@admin.route("/venues/<int:venue_id>/delete", methods=[ "POST"]) 
@admin_required
def delete_venues(venue_id):

    conn = getConnection()
    if conn is None or not conn.is_connected():
        return "DB Connection Error", 500
                
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # all events
        cursor.execute("SELECT COUNT(*) AS event_count FROM events WHERE venue_id = %s", (venue_id,))
        result = cursor.fetchone()

        if result["event_count"] > 0:
            flash("Cannot delete venue that already has an event.")
            return redirect(url_for("admin.admin_dashboard"))
        
        delete_cursor = conn.cursor()
        delete_cursor.execute("DELETE FROM venues WHERE venue_id = %s", (venue_id,))
        conn.commit()
        delete_cursor.close()
        flash("Venue deleted successfully.")
        return redirect(url_for("admin.admin_dashboard"))
    
    except Exception as e:
        conn.rollback()
        print(f"Delete venue error: {e}")
        return "Failed to delete venue", 500
    finally:
        if cursor:
            cursor.close()
        conn.close()