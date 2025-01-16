import mariadb
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet

import logging
from typing import Any, Text, Dict, List, Type
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import (
    TEXT,
    # TEXT_TOKENS,
    # ENTITY_ATTRIBUTE_TYPE,
    # ENTITY_ATTRIBUTE_START,
    # ENTITY_ATTRIBUTE_END,
    # ENTITY_ATTRIBUTE_VALUE,
    # ENTITIES,
)

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False
)
class CustomEntityExtractor(GraphComponent):
    @classmethod
    def required_components(cls) -> List[Type]:
        return []

    @staticmethod
    def required_packages() -> List[Text]:
        return ["mariadb", "fuzzyset"]

    def __init__(
        self,
        config: Dict[Text, Any],
        name: Text,
        model_storage: ModelStorage,
        resource: Resource,
    ) -> None:
        self.dbConfig = {
            "host" : "localhost",
            "user" : "root",
            "password" : "",
            "database" : "ect_chatbot"
        }
        
        self.queries = {
            "tname" : "SELECT name FROM user WHERE role = 't';",
            "sname" : "SELECT name FROM subject;"
        }
        self.minimum_confidence = config.get("minimumConfidence", 0.8)
        self.fuzzy_sets = {}
        self.fuzzy_sets2 = {
            "year" : FuzzySet(),
            "term" : FuzzySet()
        }
        self.fuzzy_sets2["year"].add("ปี")
        self.fuzzy_sets2["term"].add("เทอม")
        self.fuzzy_sets2["term"].add("ภาค")
        self._get_entity_groups(self.dbConfig, self.queries)
        
    def train(self, training_data: TrainingData) -> Resource:
        pass

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(config, execution_context.node_name, model_storage, resource)


    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            extracted = self.match_entities(message)
            message.set("entities", message.get("entities", []) + extracted, add_to_output=True)
        return messages
    
    def _get_entity_groups(self, database_config: Dict[Text, Text], database_queries: Dict[Text, Text]):
        db = mariadb.connect(
            host=database_config["host"],
            user=database_config["user"],
            passwd=database_config["password"],
            db=database_config["database"]
        )
        cur = db.cursor()
        print(f"Queries are: {database_queries.keys()}")
        for entity_key in self.queries.keys():
            cur.execute(database_queries[entity_key])
            current_entity = FuzzySet()
            for row in cur.fetchall():
                if len(row) != 1: raise SyntaxError(f"{entity_key}: query returned more than one column!")
                current_entity.add(row[0])
            self.fuzzy_sets[entity_key] = current_entity
        db.close()

    def match_entities(self, message: Message):
        extracted_entities = []
        tokens = message.get(TEXT)
        current_entity = [0.0,""]
        current_entity_type = ""
        from pythainlp import word_tokenize
        tokens = word_tokenize(message.get(TEXT),keep_whitespace=False)
        # print("Token = " + tokens)
        # tokens = message.get(TEXT_TOKENS)
        if tokens is not None:
            for token in range(len(tokens)):
                for number_type in self.fuzzy_sets2.keys():
                    match_number_type = self.fuzzy_sets2[number_type].get(tokens[token])
                    if match_number_type is not None:
                        for type_match in match_number_type:
                            if type_match[0] > 0.8:
                                for num in range(token+1,len(tokens)):
                                    if(tokens[num].isdecimal()):
                                        entity = {
                                            "start": None,
                                            "end": None,
                                            "value": tokens[num],
                                            "entity": number_type,
                                            "confidence": type_match[0],
                                            "extractor": "ECTEntityExtractor"
                                        }
                                        extracted_entities.append(entity)
                                        break

            for tokenindex in range(len(tokens)):
                tokencurrent = tokens[tokenindex]
                for tokenindex2 in range(tokenindex + 1, len(tokens)):
                    tokencurrent += tokens[tokenindex2]
                    for entity_type in self.fuzzy_sets.keys():
                        fuzzy_matches = self.fuzzy_sets[entity_type].get(tokencurrent)
                        if fuzzy_matches is not None:
                            for match in fuzzy_matches:
                                if match[0] >= self.minimum_confidence:
                                    print(tokencurrent + " => Entity : " + match[1] + " with " + str(match[0]) + " confidence")
                                    if(match[0] > current_entity[0]):
                                        current_entity[0] = match[0]
                                        current_entity[1] = match[1]
                                        current_entity_type = entity_type
        
        if current_entity != [0.0,""]:
            entity = {
                "start": None,
                "end": None,
                "value": current_entity[1],
                "entity": current_entity_type,
                "confidence": current_entity[0],
                "extractor": "ECTEntityExtractor"
            }
            extracted_entities.append(entity)
        return extracted_entities