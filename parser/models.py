from dataclasses import dataclass, field
from typing import List


@dataclass
class FunctionalRequirement:
    id: str
    linked_sr: str
    completion_state: str
    description: str
    body: str = ""


@dataclass
class SystemFeature:
    id: str
    description: str
    functional_requirements: List[FunctionalRequirement] = field(default_factory=list)
