import mariadb
from pythainlp import word_tokenize
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet

queries = {
            "tname" : "SELECT name FROM user WHERE role = 't';",
            "sname" : "SELECT name FROM subject;"
        }
minimum_confidence = 0.8
fuzzy_sets = {}

message = "วิชาโครงการ 2 กี่หน่วยกิต"
words = word_tokenize(message,keep_whitespace=False)

print(words)

db = mariadb.connect(
                        host="localhost", 
                        user="root", 
                        passwd="", 
                        database="ect_chatbot"
                    )
# cur = db.cursor()
# cur.execute("SELECT name FROM subject;")
# result = cur.fetchall()
# print(result)

entities = []

cur = db.cursor()
print(f"Queries are: {queries.keys()}")
for entity_key in queries.keys():
#     print(queries[entity_key])
    cur.execute(queries[entity_key])
    current_entity = FuzzySet()
    for row in cur.fetchall():
        if len(row) != 1: print("{entity_key}: query returned more than one column!")
        current_entity.add(row[0])
    fuzzy_sets[entity_key] = current_entity
db.close()

extracted_entities = []
tokens = words
for token in tokens:
    for entity_type in fuzzy_sets.keys():
        fuzzy_matches = fuzzy_sets[entity_type].get(token)
        print(fuzzy_matches)
        for match in fuzzy_matches:
            if match[0] < minimum_confidence: continue
            entity = {
                "start": token.start,
                "end": token.end,
                "value": match[1],
                "confidence": match[0],
                "entity": entity_type,
            }
            extracted_entities.append(entity)

print(extracted_entities)