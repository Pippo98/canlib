import errno
import json
from pathlib import Path
from typing import List, Optional

from jsonschema import validate

def load_json(path: Path, validation_schema_path:  Optional[Path]=None) -> dict:
    with open(path, "r") as file:
        data = json.load(file)

    if validation_schema_path is not None:
        with open(validation_schema_path, "r") as file:
            schema = json.load(file)
        validate(data, schema)

    return data


def create_subtree(path: Path) -> None:
    if not path.exists():
        try:
            path.mkdir(parents=True)
        except OSError as exception:  # Guard against race condition
            if exception.errno != errno.EEXIST:
                raise exception