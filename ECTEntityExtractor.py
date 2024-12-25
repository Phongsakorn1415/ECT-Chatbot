import logging

from typing import Any, Dict, List, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

import mariadb
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False
)
class CustomEntityExtractor(GraphComponent):
    def __init__(self, config: Dict[Text, Any]):
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
        self._get_entity_groups(self.dbConfig, self.queries)

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
    ) -> GraphComponent:
        return cls(config)

    def train(self, training_data: TrainingData) -> Resource:
        pass
    
    def process(self, messages: List[Message]) -> List[Message]:
        extracted = self.match_entities(messages)
        messages.set("entities", messages.get("entities", []) + extracted, add_to_output=True)
        return messages

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mariadb", "fuzzyset"]
    
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
        tokens = message.get("tokens")
        for token in tokens:
            for entity_type in self.fuzzy_sets.keys():
                fuzzy_matches = self.fuzzy_sets[entity_type].get(token.text)
                for match in fuzzy_matches:
                    if match[0] < self.minimum_confidence: continue
                    entity = {
                        "start": token.start,
                        "end": token.end,
                        "value": match[1],
                        "confidence": match[0],
                        "entity": entity_type,
                    }
                    extracted_entities.append(entity)    
        return extracted_entities