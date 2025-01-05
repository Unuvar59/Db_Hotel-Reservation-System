import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="admin",
        password="123456",
        database="hotel_reservation"
    )