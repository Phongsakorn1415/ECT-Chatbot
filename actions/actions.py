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

        courseYear = next(tracker.get_latest_entity_values("course_year"), None)
        try:
            if not courseYear:
                mycursor = conn.cursor()
                sql = "SELECT * FROM course_year ORDER BY year"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                if mycursor.rowcount > 1:
                    buttons = []
                    for x in results:
                        title = f"{x[2]}"
                        payload = '/ask_term_price_all{"course_year": "' + str(x[2]) + '"}'
                        buttons.append({"title": title, "payload": payload})
                    dispatcher.utter_message(text="กรุณาเลือกปีของหลักสูตร:", buttons=buttons)
                    return []
                else:
                    for x in results:
                        courseYear = x[1]
                mycursor.close()
            

            
            mycursor = conn.cursor()
            sql = """
            SELECT course_year.year,education_year.year,education_year.term,educationfee.price,educationfee.per,educationfee.detail FROM educationfee
            INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
            INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
            WHERE course_year.year = %s 
            ORDER BY education_year.year,education_year.term"""
            mycursor.execute(sql,(courseYear,)) 
            results = mycursor.fetchall()
            if mycursor.rowcount < 1:
                sql = "SELECT * FROM course_year ORDER BY year"
                mycursor.execute(sql)
                results = mycursor.fetchall()
                resText = f"หลักสูตรปี {courseYear} ยังไม่มีข้อมูลค่ะ  \nกรุณาเลือกปีของหลักสูตรค่ะ"
                buttons = []
                for x in results:
                    title = f"{x[1]}"
                    payload = '/ask_term_price_all{"course_year": "' + str(x[1]) + '"}'
                    buttons.append({"title": title, "payload": payload})
                dispatcher.utter_message(text=resText, buttons=buttons)
                return []
            respon = "หลักสูตรปี "+ str(results[0][0]) +"  \n"
            lastrespon = ""
            for x in results:
                if x[1] == 0:
                    lastrespon = "ค่าปรับลงทะเบียนเรียนช้า " + str(x[3]) + " บาทต่อ" + x[4] + " " + str(x[5])
                elif x[2] == 3:
                    respon = respon + "ปีที่ " + str(x[1]) + " ซัมเมอร์ ค่าเทอม " + str(x[3]) + " บาท  \n"
                else:
                    respon = respon + "ปีที่ " + str(x[1]) + " เทอมที่ " + str(x[2]) + " ค่าเทอม " + str(x[3]) + " บาท  \n"
            
            respon += lastrespon
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            # dispatcher.utter_message(text = str(e))

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
            '3': '3',
            '4': '4',
            'หนึ่ง': '1',
            'สอง': '2',
            'สาม': '3',
            'สี่': '4'
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

        year = next(tracker.get_latest_entity_values("year"), None)
        term = next(tracker.get_latest_entity_values("term"), None)
        courseYear = next(tracker.get_latest_entity_values("course_year"), None)

        try:

            # year = yearCheck[next(tracker.get_latest_entity_values("year"), None)]
            # term = termCheck[next(tracker.get_latest_entity_values("term"), None)]
            

            # if not year or not term:
            #     mycursor = conn.cursor()
            #     sql = "SELECT year,term FROM education_year ORDER BY year,term"
            #     mycursor.execute(sql) 
            #     results = mycursor.fetchall()
            #     if mycursor.rowcount > 1:
            #         buttons = []
            #         for x in results:
            #             title = f"{x[1]}"
            #             payload = '/ask_term_price_one{"course_year": "' + str(x[1]) + '"}'
            #             buttons.append({"title": title, "payload": payload})
            #         dispatcher.utter_message(text="กรุณาเลือกปีของหลักสูตร:", buttons=buttons)
            #         return []
            
            #     else:
            #         for x in results:
            #             courseYear = x[1]
            #     mycursor.close()
            
            # if not courseYear:
            #     mycursor = conn.cursor()
            #     sql = "SELECT * FROM course_year ORDER BY year"
            #     mycursor.execute(sql) 
            #     results = mycursor.fetchall()
            #     if mycursor.rowcount > 1:
            #         buttons = []
            #         for x in results:
            #             title = f"{x[1]}"
            #             payload = '/ask_term_price_one{"course_year": "' + str(x[1]) + '"}'
            #             buttons.append({"title": title, "payload": payload})
            #         dispatcher.utter_message(text="กรุณาเลือกปีของหลักสูตร:", buttons=buttons)
            #         return []
            
            #     else:
            #         for x in results:
            #             courseYear = x[1]
            #     mycursor.close()

            mycursor = conn.cursor()
            sql = """SELECT education_year.year,education_year.term,educationfee.price,educationfee.detail FROM educationfee
            INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
            INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
            WHERE course_year.year = '2565' AND education_year.year = '%s' AND education_year.term = '%s'"""
            mycursor.execute(sql,(year,term,)) 
            results = mycursor.fetchall()
            respon = "ปี " + str(results[0][0]) + " เทอม " + str(results[0][1]) + " ค่าเทอม " + str(results[0][2]) + " บาท \nโดยแบ่งเป็น\n" + results[0][3]

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
            sql = """SELECT educationfee.price,educationfee.per,educationfee.detail FROM educationfee
            INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
            INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
            WHERE course_year.year = '2565' AND education_year.year = '0' AND education_year.term = '0'"""
            mycursor.execute(sql) 
            results = mycursor.fetchall()
            respon = "ค่าปรับลงทะเบียนเรียนช้า " + str(results[0][0]) + " บาทต่อ" + results[0][1] + " " + results[0][2]
            dispatcher.utter_message(text = respon)

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = str(e))

        return []