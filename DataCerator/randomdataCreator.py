import random
from faker import Faker

fake = Faker()

customers = [
    {
        "customer_id": i,
        "name": fake.name(),
        "phone": fake.phone_number(),
        "e_mail": fake.email(),
    }
    for i in range(1, 21)
]

rooms = [
    {
        "room_id": i,
        "type": random.choice(["Single", "Double", "Suite"]),
        "pricing": round(random.uniform(50, 300), 2),
        "capacity": random.randint(1, 4),
    }
    for i in range(1, 21)
]

employees = [
    {
        "employee_id": i,
        "name": fake.name(),
        "position": random.choice(["Manager", "Chef", "Receptionist", "Housekeeper"]),
        "contact": fake.phone_number(),
    }
    for i in range(1, 8)
]

events = [
    {
        "event_id": i,
        "event_name": fake.word().capitalize() + " Event",
        "date": fake.date_between(start_date="-1y", end_date="+1y"),
        "participation_fee": round(random.uniform(20, 200), 2),
    }
    for i in range(1, 7)
]

reservations = [
    {
        "reservation_id": i,
        "customer_id": random.choice(customers)["customer_id"],
        "room_id": random.choice(rooms)["room_id"],
        "check_in_date": fake.date_between(start_date="-1y", end_date="today"),
        "check_out_date": fake.date_between(start_date="today", end_date="+1y"),
    }
    for i in range(1, 16)
]

payments = [
    {
        "payment_id": i,
        "reservation_id": reservation["reservation_id"],
        "amount": round(random.uniform(50, 1000), 2),
        "payment_date": fake.date_between(
            start_date=reservation["check_in_date"],
            end_date=reservation["check_out_date"]
        ),
    }
    for i, reservation in enumerate(reservations, start=1)
]

roomservices = [
    {
        "service_id": i,
        "room_id": random.choice(rooms)["room_id"],
        "service_type": random.choice(["WiFi", "Breakfast", "Cleaning"]),
        "cost": round(random.uniform(10, 50), 2),
    }
    for i in range(1, 11)
]

feedbacks = [
    {
        "feedback_id": i,
        "customer_id": random.choice(customers)["customer_id"],
        "feedback_details": fake.sentence(nb_words=10),
        "feedback_date": fake.date_between(start_date="-1y", end_date="today"),
    }
    for i in range(1, 6)
]

customerevents = [
    {
        "customer_id": random.choice(customers)["customer_id"],
        "event_id": random.choice(events)["event_id"],
    }
    for i in range(1, 11)
]

def generate_sql_insert(table, rows):
    keys = rows[0].keys()
    sql = f"INSERT INTO {table} ({', '.join(keys)}) VALUES\n"
    values = ",\n".join(
        f"({', '.join(repr(row[k]) for k in keys)})" for row in rows
    )
    return sql + values + ";"

print(generate_sql_insert("customers", customers))
print(generate_sql_insert("rooms", rooms))
print(generate_sql_insert("employees", employees))
print(generate_sql_insert("events", events))
print(generate_sql_insert("reservations", reservations))
print(generate_sql_insert("payments", payments))
print(generate_sql_insert("roomservices", roomservices))
print(generate_sql_insert("feedback", feedbacks))
print(generate_sql_insert("customerevent", customerevents))
