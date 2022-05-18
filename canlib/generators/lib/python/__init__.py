import math
from pathlib import Path

import jinja2 as j2

from canlib import config
from canlib.common.network import Network
from canlib.generators.lib.schema import BitSet, Enum, Field, Message, Number, Schema

BASE_DIR = Path(__file__).parent

TEMPLATE_IDS = j2.Template((BASE_DIR / "ids.py.j2").read_text())
TEMPLATE_NETWORK = j2.Template((BASE_DIR / "network.py.j2").read_text())


def generate(network: Network, schema: Schema, output_path: Path):
    init_path = output_path / "__init__.py"
    init_path.touch()

    ids_path = output_path / "ids.py"
    ids_path.write_text(TEMPLATE_IDS.render(network=network, schema=schema))

    network_path = output_path / "network.py"
    network_path.write_text(
        TEMPLATE_NETWORK.render(
            network=network,
            schema=schema,
            serialize=serialize,
            deserialize=deserialize,
        )
    )


def casts(network: Network, field: Field):
    return network.name + "_" + field.type.name


def struct_schema(field: Field):
    if isinstance(field.type, BitSet):
        return "B" * math.ceil(field.type.size / 8)
    elif isinstance(field.type, Enum):
        return "B"
    elif isinstance(field.type, Number):
        match field.type.name:
            case "uint8":
                return "B"
            case "uint16":
                return "H"
            case "uint32":
                return "I"
            case "uint64":
                return "Q"
            case "int8":
                return "b"
            case "int16":
                return "h"
            case "int32":
                return "i"
            case "int64":
                return "q"
            case "float32":
                return "f"
            case "float64":
                return "d"
            case "bool":
                return "B"
            case _:
                raise ValueError(f"{field.type.name} type unsupported")


def pack_schema(alignment: dict) -> str:
    schema = "<" if config.IS_LITTLE_ENDIAN else ">"
    for items in alignment.values():
        if len(items) > 1:
            schema += "B"
        elif len(items) == 1:
            item = items[0]
            schema += struct_schema(item)

    return schema


def pack_fields(alignment: dict):
    fields = []
    for items in alignment.values():
        if len(items) > 1:
            pipe = [f"self.{item.name} << {item.shift} & 255" for item in items]
            fields.append(" | ".join(pipe))
        elif len(items) == 1:
            item = items[0]
            if item.shift == 0:
                if isinstance(item.type, BitSet):
                    for bytes in reversed(range(item.type.byte_size)):
                        fields.append(f"(int(self.{item.name}) >> {bytes*8}) & 255")
                else:
                    fields.append(f"self.{item.name}")
            else:
                fields.append(f"self.{item.name} << {item.shift} & 255")
    return ", ".join(fields)


def serialize(_: Network, message):
    if len(message.fields) == 0:
        return ""

    alignment = message.alignment
    return f'pack("{pack_schema(alignment)}", {pack_fields(alignment)})'


def unpack_schema(alignment, field_name):
    schema = "<" if config.IS_LITTLE_ENDIAN else ">"
    max_index = 0
    for index, items in alignment.items():
        if field_name in [item.name for item in items]:
            if len(items) > 1:
                schema += "B"
                max_index = index + 2
            elif len(items) == 1:
                item = items[0]
                bytes = struct_schema(item)
                schema += bytes
                max_index = index + len(bytes) + 1
        else:
            schema += "x"
    return schema[0:max_index]


def bitset_unpack(alignment: dict, field: Field):
    deserialized = []
    bytes = range(field.type.byte_size)
    index = field.alignment_index
    reversed_bytes = reversed(bytes)
    for byte, reversed_byte in zip(bytes, reversed_bytes):
        if isinstance(field.type, BitSet):
            deserialized.append(
                f'(unpack("{ unpack_schema(alignment, field.name) }", data[0:{ index+field.byte_size }])[{ byte }] << { reversed_byte*8 })'
            )
    return " | ".join(deserialized)


def deserialize_bitset(network: Network, alignment: dict, field: Field):
    return f"{casts(network, field)}(int({bitset_unpack(alignment, field)}))"


def deserialize_without_shift(network: Network, alignment: dict, field: Field):
    return f'{casts(network, field)}(unpack("{unpack_schema(alignment, field.name)}", data[0:{field.alignment_index + field.byte_size}])[0])'


def deserialize_with_shift(network: Network, alignment: dict, field: Field):
    return f'{casts(network, field)}((unpack("{unpack_schema(alignment, field.name)}", data[0:{field.alignment_index + field.byte_size}])[0] & {field.bit_mask}) >> {field.shift})'


def deserialize(network: Network, message: Message):
    result = {}

    for field in message.fields:
        alignment = message.alignment
        if isinstance(field.type, BitSet):
            result[field.name] = deserialize_bitset(network, alignment, field)
        elif field.shift == 0:
            result[field.name] = deserialize_without_shift(network, alignment, field)
        else:
            result[field.name] = deserialize_with_shift(network, alignment, field)

    return result