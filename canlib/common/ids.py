from dataclasses import dataclass
from typing import List, Optional, Tuple

class IDS:
    name: str
    id: int
    senders: List[str]
    receivers: List[str]
    priority: int

    @classmethod
    def empty(cls):
        return cls("", 0, [], [])