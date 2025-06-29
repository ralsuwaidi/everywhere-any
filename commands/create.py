import click
from dotenv import load_dotenv

from .validate import validate_requirements_command
from .objects import create_objects_command

load_dotenv()


@click.command()
@click.option("--space-name", required=True, help="The name of the Anytype space.")
@click.option(
    "--sf-type-key", default="page", help="The type key for SystemFeature objects."
)
@click.option(
    "--fr-type-key",
    default="task",
    help="The type key for FunctionalRequirement objects.",
)
@click.option(
    "--file-path",
    default="requirements.md",
    help="The path to the requirements markdown file.",
)
@click.pass_context
def create(ctx, space_name, sf_type_key, fr_type_key, file_path):
    """Parse a requirements file and create objects in Anytype."""
    ctx.invoke(validate_requirements_command, file_path=file_path)
    ctx.invoke(
        create_objects_command,
        space_name=space_name,
        sf_type_key=sf_type_key,
        fr_type_key=fr_type_key,
        file_path=file_path,
    )
