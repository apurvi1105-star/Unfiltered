import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="unfiltered"
)
print("Database connected successfully!")