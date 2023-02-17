from pathlib import Path

import click

from canlib import generators


@click.group()
def main():
    pass

@main.command()
@click.argument("net", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("out", type=click.Path(exists=True, file_okay=False, path_type=Path))
def generate_all(net: Path, out: Path):
    generators.loader.load_networks(net)


if __name__ == "__main__":
    main()
