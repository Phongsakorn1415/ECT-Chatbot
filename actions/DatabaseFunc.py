import mysql.connector

class DatabaseFunc:
    
    def get_connection():
        return mysql.connector.connect(
            host="localhost", 
            user="root", 
            passwd="", 
            database="ect_chatbot"
        )
    
    def DBfetch(sql: str, params: tuple = ()):
        conn = DatabaseFunc.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()  # Make sure to close the connection
        return results

    def insert_ask_answer_msg(user_msg: str,bot_msg: str):
        conn = DatabaseFunc.get_connection()
        cursor = conn.cursor()
        sql = ""
        cursor.execute(sql,(user_msg,bot_msg,))
        conn.commit()
        conn.close()