import logging
import mariadb
from typing import Any, Dict, List, Text

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False
)
class CustomEntityExtractor(GraphComponent):
    def __init__(self, component_config: Dict[Text, Any]):
        self.queries = component_config.get("queries", {})
        self.minimum_confidence = component_config.get("minimumConfidence", 0.8)
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
        # ไม่จำเป็นต้อง train ใน component นี้
        pass
    
    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            text = message.get("text") # ข้อความที่ผ่าน tokenizer แล้ว
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
                    data = [row[0] for row in cursor]
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