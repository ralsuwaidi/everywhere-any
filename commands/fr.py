import datetime

import click
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
    "--fr-name", required=True, help="The name of the Functional Requirement."
)
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
    default="6829be190dd8772c7c96a583",
    help="The type key for FunctionalRequirement objects.",
)
@click.option(
    "--system-feature-id",
    help="The ID of the related System Feature object.",
)
@click.option(
    "--system-feature-name",
    help="The name of the related System Feature object.",
)
@click.option(
    "--system-feature-type-key",
    default="bafyreiczbkx2ungqnhdf6c7haiq3efjvpb3cqm5tyfnpei3nopbexf7o2e",
    help="The type key for System Feature objects.",
)
@click.option("--links", help="A comma-separated list of object IDs to link.")
@click.option(
    "--template-id",
    default="bafyreidchi3wlbchypmpp3tksocuxzyh6hozuar4vihogm7jg7ps53yzby",
    help="The ID of the template to use for the FR.",
)
def create_fr(
    space_name,
    fr_name,
    fr_description,
    fr_status,
    fr_type_key,
    system_feature_id,
    system_feature_name,
    system_feature_type_key,
    links,
    template_id,
):
    """Create a single Functional Requirement object in Anytype."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        properties = [
            {"key": "6829bde80dd8772c7c96a582", "text": fr_name},
            {"key": "description", "text": fr_description},
            {
                "key": "created_date",
                "date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        ]

        system_feature_object_id = None
        if system_feature_id and system_feature_name:
            click.echo(
                "Error: Please provide either --system-feature-id or --system-feature-name, not both."
            )
            return
        elif system_feature_id:
            system_feature_object_id = system_feature_id
        elif system_feature_name:
            # Search for the System Feature by name
            system_features = anytype_client.search_objects(
                space_id, system_feature_name, [system_feature_type_key]
            )
            if system_features and system_features["data"]:
                # Assuming the first match is the correct one
                system_feature_object_id = system_features["data"][0]["id"]
            else:
                click.echo(
                    f"Error: System Feature with name '{system_feature_name}' not found."
                )
                # List available System Features
                all_system_features = anytype_client.search_objects(
                    space_id, "", [system_feature_type_key]
                )
                if all_system_features and all_system_features["data"]:
                    click.echo("\nAvailable System Features:")
                    for sf_obj in all_system_features["data"]:
                        click.echo(f"- {sf_obj['name']}")
                else:
                    click.echo("No System Features found in this space.")
                return

        if system_feature_object_id:
            properties.append(
                {
                    "key": "6829c5d10dd8772c7c96a599",
                    "objects": [system_feature_object_id],
                }
            )

        if links:
            properties.append({"key": "links", "objects": links.split(",")})

        # Check if an FR with the same ID already exists
        existing_frs = anytype_client.search_objects(space_id, fr_name, [fr_type_key])
        if existing_frs and existing_frs["data"]:
            for obj in existing_frs["data"]:
                if obj["name"] == fr_name:
                    click.echo(
                        f"Error: Functional Requirement with name '{fr_name}' already exists."
                    )
                    return

        fr_payload = {
            "type_key": fr_type_key,
            "name": fr_name,
            "properties": properties,
        }
        if template_id:
            fr_payload["template_id"] = template_id

        created_fr = anytype_client.create_object(space_id, fr_payload)
        click.echo(f"✅ Created FunctionalRequirement: {created_fr['object']['id']}")

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
