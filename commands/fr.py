import click
from dotenv import load_dotenv

from anytype_api import AnytypeClient

load_dotenv()

@click.command()
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


@click.command()
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
