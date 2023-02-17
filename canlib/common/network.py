from .field import Field
from .message import Message

from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

@dataclass
class RawNetwork:
    name: str
    ids: List[int]
    reserved_ids: List[int]
    messages: List[Message]
    types: List[Field]
    topics: List[str]

@dataclass
class Network:
    name: str
    messages: List[Message]

    @classmethod
    def load(cls, name: str, path: Path, validation_schema_path: Optional[Path] = None):
        pass