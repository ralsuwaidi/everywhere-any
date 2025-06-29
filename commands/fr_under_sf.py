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
    "--sf-name",
    required=True,
    help="The name of the System Feature to associate the FR with.",
)
@click.option(
    "--fr-type-key",
    default="6829be190dd8772c7c96a583",
    help="The type key for FunctionalRequirement objects.",
)
@click.option(
    "--sf-type-key",
    default="6829c5890dd8772c7c96a596",
    help="The type key for SystemFeature objects.",
)
def create_fr_under_sf(
    space_name, fr_id, fr_description, sf_name, fr_type_key, sf_type_key
):
    """Create a Functional Requirement under a System Feature by name."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        # Search for the System Feature by name
        results = anytype_client.search_objects(space_id, sf_name, [sf_type_key])
        if not (results and results["data"]):
            click.echo(f"Error: System Feature '{sf_name}' not found.")
            return

        # Assuming the first result is the correct one
        sf_id = results["data"][0]["id"]

        # Create the Functional Requirement
        fr_payload = {
            "type_key": fr_type_key,
            "name": fr_id,
            "properties": [
                {"key": "description", "text": fr_description},
                {"key": "6829c5d10dd8772c7c96a599", "objects": [sf_id]},
            ],
        }
        created_fr = anytype_client.create_object(space_id, fr_payload)
        click.echo(
            f"✅ Created FunctionalRequirement: {created_fr['object']['id']} under System Feature '{sf_name}'"
        )

    except Exception as e:
        click.echo(f"Error: {e}")
