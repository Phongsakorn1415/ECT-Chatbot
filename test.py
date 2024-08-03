import mysql.connector

conn=mysql.connector.connect(
        host="localhost", 
        user="root", 
        passwd="", 
        database="ect_chatbot"
    )

mycursor = conn.cursor()
sql = "SELECT * FROM course_year ORDER BY year"
mycursor.execute(sql) 
results = mycursor.fetchall()

print(mycursor.rowcount)