## Bristol Community Events (BCE)

## 1. Project Overview

Bristol Community Events (BCE) is a web-based platform designed to promote, manage, and connect community events within the Bristol area.

The platform aims to make discovering, booking, and managing local events seamless for users while providing administrators with efficient tools for managing event data, venues, bookings, and reporting.

This project demonstrates full-stack web development, relational database design in 3NF, and practical backend logic such as discounts, cancellation fee rules, and waiting list handling.

## 2. Core Features

### User Features

- User registration, login, and logout
- View event listings and event details
- Filter events by category and search criteria
- Book tickets for available events
- Student discount support
- Advance booking discount support
- Booking receipt view
- Booking updates (where allowed)
- Booking cancellations with fee and refund rules
- Profile view with upcoming, past, and cancelled bookings
- Waiting list join when an event is full
- Offered place visibility in profile (where configured)

### Admin Features

- Admin login with role-based access checks
- Event management: add, edit, and delete events
- Venue management: add, edit, and delete venues
- User management: update details, reset password, and delete users (with safeguards)
- Booking status overview
- Event status overview (tickets left, fully booked or available)
- Reports for specific events (profit approximation, booking count, tickets remaining)

### Booking and Pricing Features

- Capacity validation to prevent overbooking
- Multi-day event booking support (selected day storage in `booking_items`)
- Student discount (10 percent)
- Advance booking discount tiers
- Cancellation fee policy:
    - 40+ days before event: no cancellation fee
    - 25-39 days before event: 40 percent fee
    - Under 25 days: 100 percent fee
- Simulated checkout flow (no live payment processing)

## 3. Tech Stack

- Backend: Python, Flask
- Database: MySQL
- Frontend: HTML, CSS, Bootstrap
- Templating: Jinja2
- Authentication: Flask sessions
- Security: Werkzeug password hashing
- Architecture: Flask Blueprints with a shared `base.html` template for common layout

### Python Dependencies

- Flask
- mysql-connector-python
- python-dotenv

## 4. Setup Instructions

### 1) Clone the project

```bash
git clone <your-repo-url>
cd bce-assessment
```

### 2) Create and activate a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` yet, create one with:

```txt
Flask
mysql-connector-python
python-dotenv
```

Then run:

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Create a `.env` file:

```env
FLASK_SECRET_KEY=your_secret_key
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
```

### 5) Configure database

- Create the MySQL database
- Run your schema script
- Run seed data script (optional)

### 6) Run the app

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## 5. Database Design

**Top-down Approach**

**Conceptual Design**

**Entities**
- Event
- User
- Booking
- Venue
- BookingItem
- Category

**Attributes**
- Event
    - event_id 
    - name
    - start_date
    - end_date
    - price
    - venue_id
    - last_date_booking
    - description
    - is_free
- User
    - user_id 
    - name
    - role
    - email
    - password
    - is_student
    - created_at
- Booking
    - booking_id 
    - user_id
    - event_id
    - booking_date
    - total_price
    - status
- Venue
    - venue_id
    - name
    - address
    - capacity
- BookingItem
    - booking_item_id
    - booking_id
    - event_day
    - quantity
    - unit_price
- Category
    - category_id
    - name

**Relationship and cardinality**

User & Booking
    
    - user can make more than one booking
    - one booking cannot belong to more users
    - User (1) → (N) Booking
    
Event & Venue
    
    - one venue can host multiple events
    - one event cannot happen at multiple venues
    - Venue (1) → (N) Event
    
Event & Booking
    
    - An event can have multiple bookings
    - Event (1) → (N) Booking
    
Booking & BookingItem
    
    - one booking can include multiple items
    - one booking item cannot exist without a booking
    - Booking (1) → (N) BookingItem
    
Event & Category
    
    - one category can belong to many events
    - one event can belong to more than one category
    - Category (M) → (N) Event

**Logical Design**

**UNF Table**
| booking_id | user_email | event_name | venue_name | category_list | item_list |
| --- | --- | --- | --- | --- | --- |
| B001 | [jen@email.com](mailto:jen@email.com) | Jazz Festival | Arnolfini | Music, Cultural | (Day=2025-03-12, Qty=2, Price=25); (Day=2025-03-13, Qty=1, Price=25) |
| B002 | [sam@email.com](mailto:sam@email.com) | Art Exhibition | UWE Centre | Exhibition | (Day=NULL, Qty=3, Price=0) |

Aim of **1NF**

- remove repeating groups
- turn lists into rows so every cell has one value
- split them into separate tables

| booking_item_id | booking_id | event_day | quantity | unit_price |
| --- | --- | --- | --- | --- |
| BI001 | B001 | 2025-03-12 | 2 | 25.00 |
| BI002 | B001 | 2025-03-13 | 1 | 25.00 |
| BI003 | B002 | NULL | 3 | 0.00 |

| event_id | category |
| --- | --- |
| E001 | Music |
| E001 | Cultural |
| E002 | Exhibition |

Aim of **2NF**
- no partial dependencies 
    - All tables with composite keys were reviewed. No non-key attributes depend on only part of a composite primary key.

Aim of **3NF**
- no transitive dependency
- non-key should not depend on another non-key
    - User, venue, and category details are stored in dedicated tables and referenced using foreign keys.
    - If events stored venue capacity, then:
event_id → venue_id and venue_id → capacity, so event_id → capacity (transitive dependency).

    BCE avoids this by storing capacity only in venues and referencing venues from events:
    - venues(venue_id, capacity)
    - events(event_id, venue_id)

<img width="917" height="708" alt="erdiagram" src="https://github.com/user-attachments/assets/cf6b9080-ff54-4fff-be07-d477e0726c14" />



**Physical Database**

The schema is implemented in MySQL.

## 6. Security Measures

### SQL Injection Prevention

- Parameterized SQL queries (`%s`) are used throughout the backend.
- User input is not concatenated directly into SQL strings.

Example:

```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

### XSS Mitigation

- Jinja templates auto-escape output by default.
- User content is rendered as escaped text unless explicitly marked otherwise.
- Unsafe rendering for user-controlled content is avoided.

### Authentication and Authorization

- Session-based login is used for authentication.
- Role checks are applied to admin-only routes.
- Passwords are stored as hashes using Werkzeug.

## 7. Legal, Ethical, Social, and Professional Considerations

### Legal

- Privacy Policy and Terms and Conditions pages are included.
- The project is educational and does not process real commercial payments.
- Only necessary account and booking data is collected.

### Ethical

- Clear disclosure of booking, discount, and cancellation rules.
- Passwords are securely stored as hashes.
- Simulated payment flow is communicated transparently.

### Social

- Simple and responsive UI for accessibility.
- Support for free events and discounted access.
- Community-focused design intended for broad user access.

### Professional

- Separation of user and admin concerns.
- Structured database design in 3NF.
- Input validation and error handling across core routes.

## 8. Limitations and Future Improvements

- Full waiting-list acceptance workflow can be expanded
- Email notifications for booking and waiting-list events can be added
- CSRF protection can be strengthened
- More advanced reporting and analytics can be added
- UI/UX refinements can improve usability further

## 9. Final Note

This project demonstrates practical integration of:

- Flask routing and template rendering
- MySQL relational design and normalization
- User/admin authentication and role control
- Booking business logic, discounts, cancellations, and waiting list handling

