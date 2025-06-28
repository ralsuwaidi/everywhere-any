import json
import sys
from parser.exporter import export_to_json
from parser.parser import parse_lines
from parser.reader import read_markdown
from parser.stats import print_stats, validate_frs

import click
import questionary
from dotenv import load_dotenv

from anytype_api import AnytypeClient

load_dotenv()


@click.group()
def cli():
    """A command-line tool for interacting with Anytype."""
    pass


@cli.command()
@click.option("--space-name", required=True, help="The name of the Anytype space.")
@click.option(
    "--sf-type-key", default="page", help="The type key for SystemFeature objects."
)
@click.option(
    "--fr-type-key",
    default="task",
    help="The type key for FunctionalRequirement objects.",
)
def create(space_name, sf_type_key, fr_type_key):
    """Parse a requirements file and create objects in Anytype."""
    # Read and parse markdown
    lines = read_markdown("requirements.md")
    features = parse_lines(lines)

    # Output JSON
    export_to_json(features, "requirements.json")
    click.echo("✅ Requirements exported to requirements.json")

    # Print stats
    print_stats(features)

    # Validate FR count
    with open("requirements.md", "r") as f:
        md_text = f.read()
    validate_frs(features, md_text)

    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        for feature in features:
            sf_payload = {
                "type_key": sf_type_key,
                "name": feature.id,
                "properties": [{"key": "description", "text": feature.description}],
            }
            created_sf = anytype_client.create_object(space_id, sf_payload)
            click.echo(f"Created SystemFeature: {created_sf['id']}")

            fr_ids = []
            for fr in feature.functional_requirements:
                fr_payload = {
                    "type_key": fr_type_key,
                    "name": fr.id,
                    "properties": [
                        {"key": "description", "text": fr.description},
                        {"key": "status", "select": fr.completion_state},
                    ],
                }
                created_fr = anytype_client.create_object(space_id, fr_payload)
                click.echo(f"  Created FunctionalRequirement: {created_fr['id']}")
                fr_ids.append(created_fr["id"])

            sf_update_payload = {
                "properties": [{"key": "functionalRequirements", "objects": fr_ids}]
            }
            anytype_client.update_object(created_sf["id"], sf_update_payload)

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
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
                        "name": f"{obj_type['name']} (Key: {obj_type['key']})",
                        "value": obj_type["key"],
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
                obj_type["key"].lower(): obj_type["key"]
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


@cli.command()
@click.option(
    "--space-name",
    required=True,
    help="The name of the Anytype space.",
)
@click.option("--fr-id", required=True, help="The ID of the Functional Requirement.")
@click.option(
    "--fr-description",
    required=True,
    help="The description of the Functional Requirement.",
)
@click.option(
    "--fr-status",
    default="To Do",
    help="The status of the Functional Requirement (e.g., 'To Do', 'In Progress', 'Done').",
)
@click.option(
    "--fr-type-key",
    default="task",
    help="The type key for FunctionalRequirement objects.",
)
def create_fr(space_name, fr_id, fr_description, fr_status, fr_type_key):
    """Create a single Functional Requirement object in Anytype."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        fr_payload = {
            "type_key": fr_type_key,
            "name": fr_id,
            "properties": [
                {"key": "description", "text": fr_description},
                {"key": "status", "select": fr_status},
            ],
        }
        created_fr = anytype_client.create_object(space_id, fr_payload)
        click.echo(f"✅ Created FunctionalRequirement: {created_fr['id']}")

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.option(
    "--space-name",
    default="Everywhere",
    required=True,
    help="The name of the Anytype space.",
)
@click.option(
    "--fr-type-key",
    default="task",
    help="The type key for FunctionalRequirement objects.",
)
def list_frs(space_name, fr_type_key):
    """List all Functional Requirements in a given space."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        results = anytype_client.search_objects(space_id, "", [fr_type_key])
        click.echo(f"\n--- Functional Requirements in '{space_name}' ---")
        if results and results["data"]:
            for obj in results["data"]:
                description = ""
                for prop in obj.get("properties", []):
                    if prop.get("key") == "description":
                        description = prop.get("text", "")
                        break
                click.echo(f"- {obj['name']} ({obj['type']['name']}) - {description}")
        else:
            click.echo("No Functional Requirements found for the given type key.")
            click.echo("\n--- Available Object Types ---")
            object_types = anytype_client.get_object_types(space_id)
            if object_types and object_types["data"]:
                for obj_type in object_types["data"]:
                    click.echo(f"- {obj_type['name']} (Key: {obj_type['key']})")
            else:
                click.echo("No object types found in this space.")

    except Exception as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.option(
    "--space-name",
    default="Everywhere",
    help="The name of the Anytype space.",
)
@click.option(
    "--type-key",
    help="The key of the object type to get details for.",
)
def get_type_details(space_name, type_key):
    """Get details of a specific object type in an Anytype space."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        if not type_key:
            object_types = anytype_client.get_object_types(space_id)
            if not (object_types and object_types["data"]):
                click.echo("No object types found in this space.")
                return
            if not sys.stdin.isatty():
                click.echo("Available object types:")
                for obj_type in object_types["data"]:
                    click.echo(f"- {obj_type['name']} (Key: {obj_type['key']})")
                click.echo(
                    "\nError: --type-key is required when not running in an interactive terminal."
                )
                return

            choices = []
            for obj_type in object_types["data"]:
                choices.append(
                    {
                        "name": f"{obj_type['name']} (Key: {obj_type['key']})",
                        "value": obj_type["id"],
                    }
                )
            selected_type_key = questionary.select(
                "Select an object type:",
                choices=choices,
                instruction="Use arrow keys to navigate, enter to confirm.",
            ).ask()
            if not selected_type_key:
                click.echo("No type selected. Exiting.")
                return
            type_key = selected_type_key

        type_details = anytype_client.get_object_type(space_id, type_key)
        if type_details:
            click.echo(f"\n--- Details for Type: {type_details} (Key: ) ---")
            click.echo(json.dumps(type_details, indent=2))
        else:
            click.echo(f"Error: Type '{type_key}' not found in space '{space_name}'.")

    except Exception as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
