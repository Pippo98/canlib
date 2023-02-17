from typing import List, Optional, Tuple
from pathlib import Path

from parse import *

from canlib.common.message import Message
from canlib.common.field import Field

from dataclasses import dataclass

@dataclass
class DBC:
    name : str
    version: str

    bus_speed: int
    can_nodes: List[str]


    names: List[str]
    messages: List[Message]

    @classmethod
    def load(cls, path: Path):
        name = path.stem
        with open(path, "r") as file:
            lines = file.readlines()
        
        messages = []
        in_messages = False
        for line in lines:
            line = line.replace("\t", " ")
            line = line.replace("\r", "")
            line = line.replace("\n", "")
            line = line.replace("  ", " ")
            line = line.replace('""', '" "')
            if line.startswith("VERSION"):
                version = line.split()[1]
            elif line.startswith("BU_:"):
                can_nodes = line.split()[1:]
            elif line.startswith("BO_"):
                in_messages = True
                msg = parse("BO_ {id:d} {name}: {length:d} {sender}", line)
                messages.append(Message(msg["name"], msg["id"], msg["sender"], []))
            elif in_messages and line.startswith(" SG_"):
                print(line)
                field = parse(' SG_ {name:w} : {start:d}|{length:d}@{endian:1}{signed:1} ({scale:g},{offset:g}) [{min:g}|{max:g}] \"{unit}\" {receiver:w}', line)
                print(field)
                field = Field(field["name"], field["start"], field["length"], field["endian"], field["signed"], field["scale"], field["offset"], field["min"], field["max"], field["unit"], field["receiver"])
                messages[-1].fields.append(field)
            elif in_messages and line.strip() == "":
                in_messages = False
            elif line.startswith("CM_"):
                pass

        return cls(name, version, 500000, can_nodes, [], messages)