import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="hotel_reservation"
    )
    if connection.is_connected():
        print(f"Connected to database: {connection.database}")
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")
finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("Connection closed.")
