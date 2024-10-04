import mysql.connector

class DBFunc:
    
    def get_connection():
        return mysql.connector.connect(
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
        sql = "INSERT INTO collected_data (user_msg, bot_msg, intent_name, confidence, DateTime) VALUES (%s, %s, %s, %s, now())"
        cursor.execute(sql,(user_msg,bot_msg,intent_name,str(confidence)))
        conn.commit()
        cursor.close
        conn.close()