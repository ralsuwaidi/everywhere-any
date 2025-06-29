import click
import questionary
import sys
from dotenv import load_dotenv

from anytype_api import AnytypeClient

load_dotenv()


@click.command()
@click.option(
    "--space-name",
    default="Everywhere",
    help="The name of the Anytype space.",
)
@click.option(
    "--object-type-id",
    help="The ID of the object type to get templates for.",
)
def list_templates(space_name, object_type_id):
    """List templates for a given object type in an Anytype space."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        if not object_type_id:
            object_types = anytype_client.get_object_types(space_id)
            if not (object_types and object_types["data"]):
                click.echo("No object types found in this space.")
                return
            if not sys.stdin.isatty():
                click.echo("Available object types:")
                for obj_type in object_types["data"]:
                    click.echo(f"- {obj_type['name']} (Key: {obj_type['key']})")
                click.echo(
                    "\nError: --object-type-id is required when not running in an interactive terminal."
                )
                return

            choices = []
            for obj_type in object_types["data"]:
                choices.append(
                    {
                        "name": f"{obj_type['name']} (ID: {obj_type['id']})",
                        "value": obj_type["id"],
                    }
                )

            selected_object_type_id = questionary.select(
                "Select an object type:",
                choices=choices,
                instruction="Use arrow keys to navigate, enter to confirm.",
            ).ask()
            if not selected_object_type_id:
                click.echo("No type selected. Exiting.")
                return
            object_type_id = selected_object_type_id

        templates = anytype_client.get_templates_for_type(space_id, object_type_id)
        click.echo(f"\n--- Templates for Object Type: {object_type_id} ---")
        if templates and templates["data"]:
            for template in templates["data"]:
                click.echo(f"- {template['name']} (ID: {template['id']})")
        else:
            click.echo("No templates found for the selected object type.")

    except Exception as e:
        click.echo(f"Error: {e}")
