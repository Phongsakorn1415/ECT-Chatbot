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
        self.queries = {
            "tname" : "SELECT name FROM user WHERE role = 't';",
            "sname" : "SELECT name FROM subject;"
        }
        self.minimum_confidence = config.get("minimumConfidence", 0.8)
        self.fuzzy_sets = {}

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
        for message in messages:
            text = message.get("text")
            entities = []
            for entity_type, query in self.queries.items():
                try:
                    conn = mariadb.connect(
                        host="localhost", 
                        user="root", 
                        passwd="", 
                        database="ect_chatbot"
                    )
                    cursor = conn.cursor()
                    cursor.execute(query)
                    data = cursor.fetchall()
                    conn.close()

                    if entity_type not in self.fuzzy_sets:
                        self.fuzzy_sets[entity_type] = FuzzySet(data)

                    match = self.fuzzy_sets[entity_type].get(text)

                    if match and match[0] >= self.minimum_confidence:
                        entities.append(
                            {
                                "entity": entity_type,
                                "value": match[1],
                                "confidence": match[0],
                                "extractor": "custom_entity_extractor",
                            }
                        )
                except mariadb.Error as e:
                    logger.error(f"Database error: {e}")
                    continue

            message.set("entities", message.get("entities", []) + entities)

        return messages

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mariadb", "fuzzyset"]