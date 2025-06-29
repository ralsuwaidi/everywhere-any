import click
from dotenv import load_dotenv

from commands.create import create
from commands.fr import create_fr, list_frs
from commands.list import list_objects, get_object_type_details
from commands.validate import validate_requirements_command
from commands.objects import create_objects_command

load_dotenv()


@click.group()
def cli():
    """A command-line tool for interacting with Anytype."""
    pass


from commands.sf import create_sf
from commands.list_templates import list_templates
from commands.import_requirements import import_requirements

cli.add_command(create)
cli.add_command(list_objects)
cli.add_command(get_object_type_details)
cli.add_command(create_fr)
cli.add_command(list_frs)
cli.add_command(validate_requirements_command)
cli.add_command(create_objects_command)
cli.add_command(create_sf)
cli.add_command(list_templates)
cli.add_command(import_requirements)

if __name__ == "__main__":
    cli()
