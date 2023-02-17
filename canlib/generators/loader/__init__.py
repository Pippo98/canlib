from canlib.common.network import Network

from typing import List, Optional, Tuple
from pathlib import Path
from pprint import pprint

from canlib.common.dbc import DBC

def load_networks(networks_dir: Path):
    networks = []

    for directory in networks_dir.iterdir():
        name = directory.name

        path = networks_dir / name / "network.json"
        assert path.exists()
        dbc_path = list((networks_dir / name).glob("*.dbc"))
        
        for dbc in dbc_path:
            new_dbc = DBC.load(dbc.absolute())
            pprint(new_dbc)
            print(len(new_dbc.messages))

    return networks