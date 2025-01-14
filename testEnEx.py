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
minimum_confidence = 0.3
fuzzy_sets = {}

message = "วิชาลีนุกซ์มีกี่หน่วยกิต"
# message = "วิชาการโปรแกรมเครือข่ายกี่หน่วยกิต"
words = word_tokenize(message)

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
    cur.execute(queries[entity_key])
    current_entity = FuzzySet()
    result = cur.fetchall()
    for row in result:
        if len(row) != 1: print("{entity_key}: query returned more than one column!")
        current_entity.add(row[0])
    fuzzy_sets[entity_key] = current_entity
db.close()

extracted_entities = []

import itertools
for token in range(len(words)):
    curToken = words[token]
    for tokenI in range(token + 1, len(words)):
        curToken += words[tokenI]
        print(curToken)
        for entity_type in fuzzy_sets.keys():
            fuzzy_matches = fuzzy_sets[entity_type].get(words[tokenI])
            print(fuzzy_matches)
            if fuzzy_matches is not None:
                for match in fuzzy_matches:
                    if match[0] < minimum_confidence: continue
                    entity = {
                        # "start": token.start,
                        # "end": token.end,
                        "value": match[1],
                        "confidence": match[0],
                        "entity": entity_type,
                    }
                    extracted_entities.append(entity)

print(extracted_entities)