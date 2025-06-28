import click
from dotenv import load_dotenv

from anytype_api import AnytypeClient
from parser.exporter import export_to_json
from parser.parser import parse_lines
from parser.reader import read_markdown
from parser.stats import print_stats, validate_frs

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
