import click
from dotenv import load_dotenv

from commands.create import create
from commands.fr import create_fr, list_frs
from commands.list import list_objects, get_object_type_details

load_dotenv()


@click.group()
def cli():
    """A command-line tool for interacting with Anytype."""
    pass


cli.add_command(create)
cli.add_command(list_objects)
cli.add_command(get_object_type_details)
cli.add_command(create_fr)
cli.add_command(list_frs)

if __name__ == "__main__":
    cli()
