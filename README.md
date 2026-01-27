## **Bristol Community Events (BCE) — Project Specification & Documentation**

### **1. Project Overview**

**Bristol Community Events (BCE)** is a web-based platform designed to promote, manage, and connect community events within the Bristol area.
The platform aims to make discovering, booking, and managing local events seamless for users while providing administrators with efficient tools for managing event data, venues, and bookings.

BCE was developed as part of an ongoing initiative to digitalise local community engagement and event participation. The system emphasises accessibility, simplicity, and responsive design.

### **Project scope**



### **2. Database Design**

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


<!-- add er diagram image -->

**Physical Database**

The schema is implemented in MySQL.

