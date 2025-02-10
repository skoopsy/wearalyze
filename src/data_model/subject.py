from .condition import Condition

from typing import Dict, Any

class Subject:
    """ Represents a subject and the conditions of their data """

    def __init__(self, subject_id: str):
        self.subject_id = subject_id
        self.conditions: Dict[str, Condition] = {}

    def add_condition(self, condition: Condition) -> None:
        self.conditions[condition.name] = condition

    def get_condition(self, condition_name: str) -> Condition:
        return self.conditions.get(condition_name)

    def __repr__(self) -> str:
        return f"Subject(subject_id={self.subject_id}, conditions={list(self.conditions.keys())})"


