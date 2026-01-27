import mysql.connector, dbfunc, sys
from mysql.connector import Error
 
""" Connect to MySQL database """
conn = dbfunc.getConnection()

if conn != None:
    if conn.is_connected():
        print('MySQL Connection is established')
        # Write your DB queries here...                    

        conn.close() #Connection must be closed
    else:
        print('DB connection error')
else:
    print('DBFunc error')
