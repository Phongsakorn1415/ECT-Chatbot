import mysql.connector

conn=mysql.connector.connect(
        host="localhost", 
        user="root", 
        passwd="", 
        database="ect_chatbot"
    )

mycursor = conn.cursor()
# sql = "SELECT course_year.year,education_year.year,education_year.term,educationfee.price,educationfee.per,educationfee.detail FROM educationfee \
#     INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id) \
#     INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id) \
#     WHERE course_year.year = '2565'  \
#     ORDER BY education_year.year,education_year.term"


mycursor.execute(sql) 
results = mycursor.fetchall()

print(results)