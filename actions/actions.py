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
import thaispellcheck
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

conn=mysql.connector.connect(
        host="localhost", 
        user="root", 
        passwd="", 
        database="ect_chatbot"
    )

class ActionAllTermPrice(Action):

    def name(self) -> Text:
        return "action_term_price_all"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            mycursor = conn.cursor()
            sql = "SELECT * FROM educationfee"
            mycursor.execute(sql) 
            results = mycursor.fetchall()
            respon = ""
            for x in results:
                if x[1] == 0:
                    lastrespon = "ค่าปรับลงทะเบียนเรียนช้า " + str(x[3]) + " บาทต่อ" + x[4] + str(x[5])
                else:
                    respon = respon + "ปีที่ " + str(x[1]) + " เทอมที่ " + str(x[2]) + " ค่าเทอม " + str(x[3]) + " บาท\n"
            
            respon += lastrespon
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")

        return []
    
class ActionOneTermPrice(Action):

    def name(self) -> Text:
        return "action_term_price_one"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        yearCheck = {
            '1': '1',
            '2': '2',
            'หนึ่ง': '1',
            'สอง': '2'
        }

        termCheck = {
            '1': '1',
            '2': '2',
            'หนึ่ง': '1',
            'สอง': '2',
            'summer': '3',
            'Summer': '3',
            'ซัมเมอร์': '3',
            'ซัมเมอ': '3'
        }

        try:
            year = yearCheck[thaispellcheck.check(tracker.get_slot("educationYear"),autocorrect=True)]
            term = termCheck[thaispellcheck.check(tracker.get_slot("educationTerm"),autocorrect=True)]
            
            mycursor = conn.cursor()
            sql = "SELECT * FROM educationfee WHERE year = '%s' AND term = '%s'"%(year,term)
            mycursor.execute(sql) 
            results = mycursor.fetchall()
            respon = "ปี " + str(results[0][1]) + " เทอม " + str(results[0][2]) + " ค่าเทอม " + str(results[0][3]) + " บาท \nโดยแบ่งเป็น\n" + results[0][5]

            dispatcher.utter_message(text = respon)

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = str(e))

        return []
    
class ActionLateFees(Action):

    def name(self) -> Text:
        return "action_term_late_fees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            mycursor = conn.cursor()
            sql = "SELECT * FROM educationfee WHERE year = '0'"
            mycursor.execute(sql) 
            results = mycursor.fetchall()
            respon = "ค่าปรับลงทะเบียนเรียนช้า " + str(results[0][3]) + " บาทต่อ" + results[0][4] + results[0][5]
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")

        return []