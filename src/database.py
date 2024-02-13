import os
from dotenv import load_dotenv, find_dotenv
import psycopg2

load_dotenv(find_dotenv())

database_connection = psycopg2.connect(
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST")
)