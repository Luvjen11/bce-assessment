import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
load_dotenv()

# MYSQL CONFIG VARIABLES
hostname = os.getenv("DB_HOST")
username = os.getenv("DB_USER")
passw = os.getenv("DB_PASSWORD")
dbase = os.getenv("DB_NAME")  

def getConnection():
    try:
        conn = mysql.connector.connect(host=hostname, user=username, password=passw, database=dbase,)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or Password is not working")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return conn