# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


# def dataFetch(command):
#     myDB=mysql.connector.conect(
#         host="localhost", 
#         user="root", 
#         passwd="", 
#         database="ect_chatbot"
#     )

#     mycursor = mydb.cursor() 
#     sql = command

#     try:
#         #Execute the SQL Query
#         mycursor.execute(sql) 
#         results = mycursor.fetchall()

#         UserName = results[0][0]
#         UserEmail = results[0][2]

#         #Now print fetched data
#         dispatcher.utter_message(f"User Name: {UserName}, User Email: {UserEmail}")

#     except:
#         dispatcher.utter_message("Error : Unable to fetch data.")
import mysql.connector
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionTermPrice(Action):

    def name(self) -> Text:
        return "action_term_price_all"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            myDB=mysql.connector.connect(
                    host="localhost", 
                    user="root", 
                    passwd="", 
                    database="ect_chatbot"
                )
            mycursor = myDB.cursor()
            sql = "SELECT * FROM educationfee"
            mycursor.execute(sql) 
            results = mycursor.fetchall()
            respon = ""
            for x in results:
                if x[1] == 0:
                    respon = respon + "ค่าปรับลงทะเบียนเรียนช้า " + str(x[3]) + " บาทต่อ" + x[4] + str(x[5])
                else:
                    respon = respon + "ปีที่ " + str(x[1]) + " เทอมที่ " + str(x[2]) + " ค่าเทอม " + str(x[3]) + " บาท\n"
            dispatcher.utter_message(text = respon)

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = str(e))

        return []