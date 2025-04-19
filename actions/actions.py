from rasa_sdk.types import DomainDict
import json
from .DatabaseFunc import DBFunc
from typing import Any, Coroutine, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

                    # buttons = []
                    # for x in results:
                    #     title = f"{x[0]}"
                    #     payload = "/ask_term_price_one{{'course_year': '" + str(x[0]) + "'}"
                    #     if year:
                    #         payload = payload + ",{'year':'" + year +"'}"
                    #     if term:
                    #         payload = payload + ",{'term':'" + term +"'}"
                    #     payload = payload + "}"
                    #     buttons.append({"title": title, "payload": payload})
                    # dispatcher.utter_message(text="กรุณาเลือกปีของหลักสูตร", buttons=buttons)
                    # return []

class ActionAllTermPrice(Action):

    def name(self) -> Text:
        return "action_term_price_all"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            respon = ""
            user_course_year = next(tracker.get_latest_entity_values("course_year"), None)
            course_year = DBFunc.get_course_year(user_course_year)
            if course_year:
                sql = """
                SELECT course_year.year,education_year.year,education_year.term,educationfee.price,educationfee.per,educationfee.detail FROM educationfee
                INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
                INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
                WHERE course_year.year = ?
                ORDER BY education_year.year,education_year.term"""
                results = DBFunc.DBfetch(sql,(course_year,))
                if results:
                    respon = "หลักสูตรปี "+ str(results[0][0]) +"  \n"
                    lastrespon = ""
                    for x in results:
                        if x[1] == 0:
                            lastrespon = "ค่าปรับลงทะเบียนเรียนช้า " + str(x[3]) + " บาทต่อ" + x[4] + " " + str(x[5])
                        else:
                            respon = respon + "ปีที่ " + str(x[1]) + " เทอมที่ " + str(x[2]) + " ค่าเทอม " + str(x[3]) + " บาท  \n"
                    
                    respon += lastrespon
                    DBFunc.insert_ask_answer_msg(
                        tracker.latest_message.get('text'), 
                        respon,
                        tracker.latest_message['intent'].get('name'), 
                        tracker.latest_message['intent'].get('confidence')
                    )
                    dispatcher.utter_message(text = respon)

                else:
                    dispatcher.utter_message(text = f"ไม่พบข้อมูลค่าเทอมของหลักสูตรปี" + user_course_year + " ค่ะ")
                
            else:
                dispatcher.utter_message(text = "ไม่พบข้อมูลของหลักสูตรปี " + user_course_year + " ค่ะ")

            

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = "action_term_price_all error : "+str(e))

        return []
    
class ActionOneTermPrice(Action):

    def name(self) -> Text:
        return "action_term_price_one"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            year = next(tracker.get_latest_entity_values("year"), None)
            term = next(tracker.get_latest_entity_values("term"), None)
            
            sql = """SELECT education_year.year,education_year.term,educationfee.price,educationfee.detail FROM educationfee
            INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
            INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
            WHERE course_year.year = '2565' AND education_year.year = ? AND education_year.term = ?"""
            results = DBFunc.DBfetch(sql,(year,term))
            respon = "ปี " + str(results[0][0]) + " เทอม " + str(results[0][1]) + " ค่าเทอม " + str(results[0][2]) + " บาท"
            if results[0][3] != '':
                respon += "\nโดยแบ่งเป็น  \n" + results[0][3].replace("\n","  \n")

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = "action_term_price_one error : "+str(e))

        return []
    
class ActionLateFees(Action):

    def name(self) -> Text:
        return "action_term_late_fees"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            sql = """SELECT educationfee.price,educationfee.per,educationfee.detail FROM educationfee
            INNER JOIN education_year ON (educationfee.educationyear_id = education_year.id)
            INNER JOIN course_year ON (educationfee.courseyear_id = course_year.id)
            WHERE course_year.year = '2565' AND education_year.year = '0' AND education_year.term = '0'"""
            results = DBFunc.DBfetch(sql)
            respon = "ค่าปรับลงทะเบียนเรียนช้า " + str(results[0][0]) + " บาทต่อ" + results[0][1] + " " + results[0][2]

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            # dispatcher.utter_message(text = "เกิดข้อผิดพลาดในการหาข้อมูล กรุณาลองใหม่อีกครั้ง")
            dispatcher.utter_message(text = str(e))

        return []
    
class ActionTeacherAll(Action):
    
    def name(self) -> Text:
        return "action_teacher_all"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            sql = """SELECT name,lastname FROM user WHERE role = 't' ORDER BY name"""
            results = DBFunc.DBfetch(sql)
            respon = "อาจารย์  \n"
            for x in results:
                respon = respon + x[0] + " " + x[1] + "  \n"
            
            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)
        
        except Exception as e:
            dispatcher.utter_message(text = str(e))

        return []

class ActionTeacherContact(Action):
    
    def name(self) -> Text:
        return "action_teacher_contact"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        tname = next(tracker.get_latest_entity_values("tname"), None)

        try:
            sql = """SELECT contact_type.type_name,contact.detail,user.title FROM contact
            INNER JOIN user ON (contact.user_id = user.id)
            INNER JOIN contact_type ON (contact.contact_type_id = contact_type.id)
            WHERE user.name = ? AND user.role = 't' ORDER BY contact_type.id"""
            results = DBFunc.DBfetch(sql,(tname,))
            if len(results) < 1:
                respon = f"อาจารย์ {tname} ไม่มีข้อมูลช่องทางติดต่อ"
                dispatcher.utter_message(text = respon)
                return []
            
            ctype = []
            for x in results:
                if x[0] not in results:
                    ctype.append(x[0])

            respon = f"นี่คือข้อมูลติดต่อของ {results[0][2]}{tname} ค่ะ  \n\n"
            for x in ctype:
                respon = respon + x + "  \n"
                for y in results:
                    if y[0] == x:
                        respon = respon + f" - {y[1]}"
                    if y == results[len(results) - 1]:
                        respon = respon + "  \n\n"

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = str(e))

        return []
    
class ActionTeacherTeach(Action):

    def name(self) -> Text:
        return "action_teacher_teach"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        tname = next(tracker.get_latest_entity_values("tname"), None)

        try:
            sql = """SELECT subject.id,subject.name FROM teach
            INNER JOIN user ON (teach.user_id = user.id)
            INNER JOIN subject ON (teach.subject_id = subject.id)
            WHERE user.name = ? AND user.role = 't' ORDER BY subject.id"""
            results = DBFunc.DBfetch(sql,(tname,))
            if len(results) < 1:
                respon = f"อาจารย์ {tname} ไม่มีข้อมูลชวิชาที่สอน"
            else:
                respon = f"นี่คือวิชาทั้งหมดที่อาจารย์ {tname} สอนค่ะ  \n"
                for x in results:
                    respon += "รหัสวิชา : " + str(x[0]) + "  \n" + x[1] + "  \n  \n"
            

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = str(e))
        
        return []

class ActionRequiredSubject(Action):
    
    def name(self) -> Text:
        return "action_required_subject"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            sql = """SELECT education_year.year,education_year.term,subject.id,subject.name FROM subject
                INNER JOIN education_year ON (subject.education_year_id = education_year.id)
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.isRequire = '1'"""
            results = DBFunc.DBfetch(sql)

            eyear = []
            for x in results:
                if [x[0],x[1]] not in eyear:
                    eyear.append([x[0],x[1]])
        
            respon = "นี่คือวิชาบังคับที่มีในหลักสูตรทั้งหมดค่ะ  \n\n"
            for x in eyear:
                respon += f"ปี {x[0]} เทอม {x[1]}  \n"
                z = 1
                for y in results:
                    if [y[0], y[1]] == x:
                        respon += f"{z} : รหัสวิชา {y[2]}  \n&nbsp;&nbsp;&nbsp;{y[3]}  \n"
                        z += 1
                respon += "  \n\n"

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "action_required_subject\n" + str(e))
        
        return []
            
class ActionElectiveSubject(Action):
    
    def name(self) -> Text:
        return "action_elective_subject"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            sql = """SELECT subject.id,subject.name FROM subject
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.isRequire = '0'"""
            results = DBFunc.DBfetch(sql)

            respon = "นี่คือวิชาเลือกทั้งหมดค่ะ  \n\n"
            y = 1
            for x in results:
                respon += f"{str(y)} : รหัสวิชา {x[0]}  \n&nbsp;&nbsp;&nbsp;{x[1]}  \n"
                y += 1

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "action_required_subject\n" + str(e))

        return []
    
class ActionSubjectOneTerm(Action):
    
    def name(self) -> Text:
        return "action_subject_one_term"
    
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
            year = yearCheck[next(tracker.get_latest_entity_values("year"), None)]
            term = termCheck[next(tracker.get_latest_entity_values("term"), None)]

            sql = """SELECT subject.id,subject.name FROM subject
                INNER JOIN education_year ON (subject.education_year_id = education_year.id)
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.isRequire = '1' AND education_year.year = ? AND education_year.term = ?"""
            results = DBFunc.DBfetch(sql,(year,term))

            respon = f"นี่คือวิชาที่มีเรียนในปี {year} เทอม {term} ค่ะ  \n\n"
            y = 1
            for x in results:
                respon += f"{y} : รหัสวิชา {x[0]}  \n&nbsp;&nbsp;&nbsp;{x[1]}  \n"
                y += 1

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "action_subject_one_term\n" + str(e))
        
        return []
    
class ActionSubjectEducationTerm(Action):
    
    def name(self) -> Text:
        return "action_subject_education_term"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sname = next(tracker.get_latest_entity_values("sname"), None)

        try:
            sql = """SELECT education_year.year,education_year.term FROM subject
                INNER JOIN education_year ON (subject.education_year_id = education_year.id)
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.name = ?"""
            results = DBFunc.DBfetch(sql,(sname,))

            respon = ""
            if not sname:
                respon = "ขออภัยค่ะ กรุณาตรวจสอบว่าชื่อวิชาพิมพ์ถูกหรือไม่ด้วยนะคะ"
            elif not results:
                respon = f"วิชา {sname} ไม่มีข้อมูลค่ะ"
            
            else:
                for x in results:
                    if x[0] == 0:
                        respon += f"วิชา {sname}  \nเป็นวิชาเลือกค่ะ ไม่มีกำหนดว่าเรียนเทอมไหนค่ะ"
                    else:
                        respon += f"วิชา {sname}  \nเรียนตอนปี {x[0]} เทอม {x[1]} ค่ะ"
            

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "IN action_subject_education_term\n ERROR => " + str(e))
        
        return []
    
class ActionSubjectLanguage(Action):
    
    def name(self) -> Text:
        return "action_subject_language"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sname = next(tracker.get_latest_entity_values("sname"), None)

        try:
            sql = """SELECT subject.language FROM subject
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.name = ?"""
            results = DBFunc.DBfetch(sql,(sname,))

            respon = ""
            if not sname:
                respon = "ขออภัยค่ะ กรุณาตรวจสอบว่าชื่อวิชาพิมพ์ถูกหรือไม่ด้วยนะคะ"
            elif not results:
                respon = f"วิชา {sname} ไม่มีข้อมูลค่ะ"
            
            else:
                for x in results:
                    if x[0] == "th":
                        respon += f"วิชา {sname}  \nเรียนเป็นภาษาไทยค่ะ"
                    elif x[0] == "en":
                        respon += f"วิชา {sname}  \nเรียนเป็นภาษาอังกฤษค่ะ"
            

            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "IN action_subject_language\n ERROR => " + str(e))
        
        return []
    
class ActionSubjectCredit(Action):
    
    def name(self) -> Text:
        return "action_subject_credit"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sname = next(tracker.get_latest_entity_values("sname"), None)

        try:
            sql = """SELECT subject.credit FROM subject
                INNER JOIN course_year ON (subject.course_year_id = course_year.id)
                WHERE course_year.year = '2565' AND subject.name = ?"""
            results = DBFunc.DBfetch(sql,(sname,))

            respon = ""
            if not sname:
                respon = "ขออภัยค่ะ กรุณาตรวจสอบว่าชื่อวิชาพิมพ์ถูกหรือไม่ด้วยนะคะ"
            elif not results:
                respon = f"วิชา {sname} ไม่มีข้อมูลค่ะ"
            else:
                for x in results:
                    respon += f"วิชา {sname}  \nมี {x[0]} หน่วยกิต"
            
            DBFunc.insert_ask_answer_msg(
                tracker.latest_message.get('text'), 
                respon,
                tracker.latest_message['intent'].get('name'), 
                tracker.latest_message['intent'].get('confidence')
            )
            dispatcher.utter_message(text = respon)

        except Exception as e:
            dispatcher.utter_message(text = "IN action_subject_credit\n ERROR => " + str(e))
        
        return []
    
class ActionSubjectLearnBefore(Action):
    
    def name(self) -> Text:
        return "action_subject_learn_before"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        sname = next(tracker.get_latest_entity_values("sname"), None)

class ActionFallBack(Action):
    
    def name(self) -> Text:
        return "action_fallback"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        userMessage = tracker.latest_message.get('text')
        ranking = tracker.latest_message['intent_ranking']
        
        try:
            conn = DBFunc.get_connection()
            mycursor = conn.cursor()
            # sql = "SELECT id FROM fallback_message WHERE message = ?"
            # mycursor.execute(sql,(userMessage,))
            # results = mycursor.fetchone()
            # if(mycursor.rowcount < 1):
            #     sql = "INSERT INTO fallback_message (message, date, count) VALUES (?, now(), 1)"
            #     mycursor.execute(sql,(userMessage,))
            #     conn.commit()
            # else:
            #     sql = "UPDATE fallback_message SET count = count + 1 WHERE id = ?"
            #     mycursor.execute(sql,(results[0],))
            #     conn.commit()

            filtered_ranking = [intent for intent in ranking if intent['name'] != 'nlu_fallback']
            top_intent = json.dumps(filtered_ranking[:3])

            sql = "INSERT INTO fallback_message (message, date, intent_ranking) VALUES (?, now(), ?)"
            mycursor.execute(sql,(userMessage,top_intent))
            conn.commit()
            mycursor.close
            conn.close()
            
            dispatcher.utter_message(text = "ขออภัยค่ะ ฉันไม่สามารถตอบคำถามของคุณได้  \nหากพิมพ์ผิด กรุณาพิมพ์ใหม่ได้ไหมคะ")
        except Exception as e:
            # dispatcher.utter_message(text = "ขออภัยค่ะ ฉันไม่สามารถตอบคำถามของคุณได้  \nหากพิมพ์ผิด กรุณาพิมพ์ใหม่ได้ไหมคะ")
            dispatcher.utter_message(text = str(e))
        
        return []