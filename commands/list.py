import json
import sys

import click
import questionary
from dotenv import load_dotenv

from anytype_api import AnytypeClient

load_dotenv()


@click.command()
@click.option(
    "--space-name", default="Everywhere", help="The name of the Anytype space."
)
@click.option("--query", default="", help="The search query.")
@click.option(
    "--type-keys", help="A comma-separated list of type keys or names to search for."
)
def list_objects(space_name, query, type_keys):
    """List objects in an Anytype space."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        if not type_keys:
            object_types = anytype_client.get_object_types(space_id)
            if not (object_types and object_types["data"]):
                click.echo("No object types found in this space.")
                return

            choices = []
            for obj_type in object_types["data"]:
                choices.append(
                    {
                        "name": f"{obj_type['name']} (ID: {obj_type['id']})",
                        "value": obj_type["id"],
                    }
                )

            type_name_or_id = questionary.select(
                "Select an object type:",
                choices=choices,
                instruction="Use arrow keys to navigate, enter to confirm.",
            ).ask()
            if not type_name_or_id:
                click.echo("No type selected. Exiting.")
                return
            type_names_or_ids = [type_name_or_id]
        else:
            type_names_or_ids = type_keys.split(",")
        resolved_type_ids = []

        object_types = anytype_client.get_object_types(space_id)
        if object_types and object_types["data"]:
            type_map = {
                obj_type["name"].lower(): obj_type["key"]
                for obj_type in object_types["data"]
            }
            type_key_map = {
                obj_type["id"].lower(): obj_type["id"]
                for obj_type in object_types["data"]
            }
        else:
            type_map = {}
            type_key_map = {}

        for key_or_name in type_names_or_ids:
            key_or_name_lower = key_or_name.lower()
            if key_or_name_lower in type_key_map:
                resolved_type_ids.append(type_key_map[key_or_name_lower])
            elif key_or_name_lower in type_map:
                resolved_type_ids.append(type_map[key_or_name_lower])
            else:
                click.echo(
                    f"Warning: Type '{key_or_name}' not found by name or ID. Skipping."
                )

        if not resolved_type_ids:
            click.echo("Error: No valid type keys or names provided.")
            return

        results = anytype_client.search_objects(space_id, query, resolved_type_ids)
        click.echo("\n--- Existing Objects ---")
        if results and results["data"]:
            for obj in results["data"]:
                description = ""
                for prop in obj.get("properties", []):
                    if prop.get("key") == "description":
                        description = prop.get("text", "")
                        break
                click.echo(f"- {obj['name']} ({obj['type']['name']}) - {description}")
        else:
            click.echo("No objects found for the given query and type keys.")

    except Exception as e:
        click.echo(f"Error: {e}")


@click.command()
@click.option(
    "--space-name",
    default="Everywhere",
    help="The name of the Anytype space.",
)
@click.option(
    "--object-type-id",
    help="The ID of the object type to get details for.",
)
def get_object_type_details(space_name, object_type_id):
    """Get details of a specific object type in an Anytype space."""
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
                    click.echo(f"- {obj_type['name']} (ID: {obj_type['id']})")
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

        type_details = anytype_client.get_object_type(space_id, object_type_id)
        if type_details:
            click.echo(json.dumps(type_details, indent=2))
        else:
            click.echo(
                f"Error: Type '{object_type_id}' not found in space '{space_name}'."
            )

    except Exception as e:
        click.echo(f"Error: {e}")
