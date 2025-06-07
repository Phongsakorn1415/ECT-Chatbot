import mariadb
try:
    from cfuzzyset import cFuzzySet as FuzzySet
except ImportError:
    from fuzzyset import FuzzySet

import logging
from typing import Any, Text, Dict, List, Type, Optional, Tuple
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import TEXT

logger = logging.getLogger(__name__)

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=True
)
class CustomEntityExtractor(GraphComponent):
    EXTRACTOR_NAME = "ECTEntityExtractor"
    
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
        self.resource = resource
        self.dbConfig = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "ect_chatbot"
        }
        
        self.queries = {
            "tname": "SELECT name FROM user WHERE role = 't';",
            "sname": "SELECT name FROM subject;"
        }

        summer_terms = [
            "summer", "Summer", "SUMMER", "ซัมเมอร์", "ซัมเมอ", 
            "ภาคฤดูร้อน", "ฤดูร้อน", "ภาคเรียนฤดูร้อน", "การศึกษาฤดูร้อน"
        ]
        
        self.minimum_confidence = config.get("minimumConfidence", 0.8)
        self.number_minimum_confidence = config.get("numberMinimumConfidence", 0.8)
        
        # Initialize fuzzy sets
        self.fuzzy_sets = {"summer": FuzzySet()}
        for s in summer_terms:
            self.fuzzy_sets["summer"].add(s)

        # Year and term indicators
        year_indicators = ["ปี", "ปีการศึกษา"]
        term_indicators = ["เทอม", "ภาค", "ภาคการศึกษา", "ภาคเรียน"]

        self.fuzzy_sets2 = {
            "year": FuzzySet(),
            "term": FuzzySet()
        }

        for y in year_indicators:
            self.fuzzy_sets2["year"].add(y)
        for t in term_indicators:
            self.fuzzy_sets2["term"].add(t)
            
        # Load entities from database
        self._get_entity_groups(self.dbConfig, self.queries)
        
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
    
    def _get_entity_groups(self, database_config: Dict[Text, Text], database_queries: Dict[Text, Text]) -> None:
        """Load entity values from database and create fuzzy sets"""
        try:
            db = mariadb.connect(
                host=database_config["host"],
                user=database_config["user"],
                passwd=database_config["password"],
                db=database_config["database"]
            )
            cur = db.cursor()
            
            logger.debug(f"Loading entities from database: {database_queries.keys()}")
            for entity_key in database_queries.keys():
                cur.execute(database_queries[entity_key])
                current_entity = FuzzySet()
                for row in cur.fetchall():
                    if len(row) != 1:
                        raise SyntaxError(f"{entity_key}: query returned more than one column!")
                    current_entity.add(row[0])
                self.fuzzy_sets[entity_key] = current_entity
            db.close()
        except Exception as e:
            logger.error(f"Error loading entities from database: {e}")
            raise

    def _create_entity(self, 
                      start: int, 
                      end: int, 
                      value: str, 
                      entity_type: str,
                      confidence: float) -> Dict[str, Any]:
        """Create entity dictionary with common format"""
        return {
            "start": start,
            "end": end,
            "value": value,
            "entity": entity_type,
            "confidence": confidence,
            "extractor": self.EXTRACTOR_NAME
        }

    def _extract_number_entities(self, 
                               tokens: List[str], 
                               msg: str) -> List[Dict[str, Any]]:
        """Extract numeric entities (years, terms) from tokenized message"""
        extracted_entities = []
        
        for token_idx in range(len(tokens)):
            for number_type in self.fuzzy_sets2.keys():
                match_number_type = self.fuzzy_sets2[number_type].get(tokens[token_idx])
                
                if match_number_type is None:
                    continue
                    
                for type_match in match_number_type:
                    if type_match[0] <= self.number_minimum_confidence:
                        continue
                        
                    # Look for following number
                    for num_idx in range(token_idx + 1, len(tokens)):
                        is_year = self.fuzzy_sets2['year'].get(tokens[num_idx])
                        is_term = self.fuzzy_sets2['term'].get(tokens[num_idx])
                        
                        # Check for conflicting type indicators
                        if (number_type == "term" and 
                            is_year is not None and 
                            is_year[0][0] > self.number_minimum_confidence):
                            break
                        elif (number_type == "year" and 
                              is_term is not None and 
                              is_term[0][0] > self.number_minimum_confidence):
                            break
                        elif tokens[num_idx].isdecimal():
                            entity_type = number_type
                            # Determine if it's a year or course year
                            if number_type == "year":
                                if len(tokens[num_idx]) != 4:
                                    entity_type = "year"
                                else:
                                    entity_type = "course_year"
                                    
                            start_pos = msg.find(tokens[num_idx])
                            end_pos = start_pos + len(tokens[num_idx])
                            
                            entity = self._create_entity(
                                start=start_pos,
                                end=end_pos,
                                value=tokens[num_idx],
                                entity_type=entity_type,
                                confidence=type_match[0]
                            )
                            
                            extracted_entities.append(entity)
                            break
                            
        return extracted_entities

    def _extract_text_entities(self, 
                             tokens: List[str], 
                             msg: str) -> List[Dict[str, Any]]:
        """Extract text-based entities using fuzzy matching"""
        extracted_entities = []
        current_entity = [0.0, ""]
        current_entity_type = ""
        start = 0
        end = 0
        
        for token_idx in range(len(tokens)):
            current_token = tokens[token_idx]
            
            # Try progressively longer token combinations
            for token_idx2 in range(token_idx + 1, len(tokens)):
                current_token += tokens[token_idx2]
                
                for entity_type in self.fuzzy_sets.keys():
                    fuzzy_matches = self.fuzzy_sets[entity_type].get(current_token)
                    
                    if fuzzy_matches is None:
                        continue
                        
                    for match in fuzzy_matches:
                        if match[0] < self.minimum_confidence:
                            continue
                            
                        logger.debug(f"Matched {current_token} => Entity: {match[1]} with {match[0]} confidence")
                        
                        # Special handling for summer term
                        if entity_type == 'summer':
                            start_pos = msg.find(current_token)
                            end_pos = start_pos + len(current_token)
                            
                            entity = self._create_entity(
                                start=start_pos,
                                end=end_pos,
                                value="3",  # Summer is always term 3
                                entity_type="term",
                                confidence=match[0]
                            )
                            
                            extracted_entities.append(entity)
                            continue
                            
                        # Track best match for other entity types
                        if match[0] > current_entity[0]:
                            current_entity[0] = match[0]
                            current_entity[1] = match[1]
                            current_entity_type = entity_type
                            start = msg.find(current_token)
                            end = start + len(current_token)
        
        # Add the best non-summer entity if found
        if current_entity != [0.0, ""]:
            entity = self._create_entity(
                start=start,
                end=end,
                value=current_entity[1],
                entity_type=current_entity_type,
                confidence=current_entity[0]
            )
            
            extracted_entities.append(entity)
            
        return extracted_entities

    def match_entities(self, message: Message) -> List[Dict[str, Any]]:
        """Extract all entities from a message"""
        msg = message.get(TEXT)
        
        # Tokenize message with Thai NLP
        from pythainlp import word_tokenize
        tokens = word_tokenize(msg, keep_whitespace=False)
        logger.debug(f"Tokens: {tokens}")
        
        if tokens is None:
            return []
            
        # Extract all types of entities
        number_entities = self._extract_number_entities(tokens, msg)
        text_entities = self._extract_text_entities(tokens, msg)
        
        return number_entities + text_entities
    
    def train(self, training_data: TrainingData) -> Resource:
        """Update entity database during training"""
        try:
            self._get_entity_groups(self.dbConfig, self.queries)
            logger.info(f"{self.EXTRACTOR_NAME} trained with fresh DB data.")
        except Exception as e:
            logger.error(f"Error during training: {e}")
        return self.resource