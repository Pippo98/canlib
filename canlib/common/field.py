from typing import List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Field:
    name: str
    bit_offset: int
    bit_len: int
    big_endian: bool
    signed: bool
    scale: float
    offset: float
    min: float
    max: float
    unit: str
    receiver: str
    description: Optional[str] = ""


class Signal(Field):
    pass
class Multiplexor(Field):
    pass
class Multiplexed(Field):
    pass
