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
@click.option("--sf-id", required=True, help="The ID of the System Feature.")
@click.option(
    "--sf-description",
    required=True,
    help="The description of the System Feature.",
)
@click.option(
    "--sf-type-key",
    default="6829c5890dd8772c7c96a596",
    help="The type key for SystemFeature objects.",
)
def create_sf(space_name, sf_id, sf_description, sf_type_key):
    """Create a single System Feature object in Anytype."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        sf_payload = {
            "type_key": sf_type_key,
            "name": sf_id,
            "properties": [
                {"key": "description", "text": sf_description},
            ],
        }
        created_sf = anytype_client.create_object(space_id, sf_payload)
        click.echo(f"✅ Created SystemFeature: {created_sf['object']['id']}")

    except Exception as e:
        click.echo(f"Error: {e}")
