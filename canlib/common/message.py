from typing import List, Optional, Tuple
from dataclasses import dataclass

from .field import Field

@dataclass
class Message:
    name: str
    id: int
    senders: List[str]
    fields: List[Field]

    @classmethod
    def empty(cls):
        return cls("", 0, [], [])