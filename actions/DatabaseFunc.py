# import mysql.connector
import mariadb

class DBFunc:
    
    def get_connection():
        return mariadb.connect(
            host="localhost", 
            user="root", 
            passwd="", 
            database="ect_chatbot"
        )
    
    def DBfetch(sql: str, params: tuple = ()):
        conn = DBFunc.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        cursor.close
        conn.close()  # Make sure to close the connection
        return results

    def insert_ask_answer_msg(user_msg: str, bot_msg: str, intent_name: str, confidence: float):
        conn = DBFunc.get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO collected_data (user_msg, bot_msg, intent_name, confidence, DateTime) VALUES (?, ?, ?, ?, now())"
        cursor.execute(sql,(user_msg,bot_msg,intent_name,str(confidence)))
        conn.commit()
        cursor.close
        conn.close()

    def get_course_year(target_year: str | None) -> str:
        # Get the appropriate course year from database.
        # If target_year is provided, returns the highest year that's less than or equal to target_year.
        # If target_year is None or no valid year found, returns the latest year in database.

        conn = DBFunc.get_connection()
        cursor = conn.cursor()
        
        if target_year:
            # Get highest year <= target_year
            cursor.execute("SELECT year FROM course_year WHERE year <= ? ORDER BY year DESC LIMIT 1", (target_year,))
        else:
            # Get latest year
            cursor.execute("SELECT year FROM course_year ORDER BY year DESC LIMIT 1")
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result[0] if result else None  # Default to None if no results
