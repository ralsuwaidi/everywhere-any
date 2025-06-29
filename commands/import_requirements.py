from parser.parser import parse_lines
from parser.reader import read_markdown

import click
from dotenv import load_dotenv

from commands.fr import create_fr
from commands.validate import validate_requirements_command

load_dotenv()


@click.command()
@click.option(
    "--requirements-file",
    default="requirements.md",
    help="Path to the requirements Markdown file.",
)
def import_requirements(requirements_file):
    """Reads and imports Functional Requirements from a Markdown file."""
    try:
        click.echo(f"Reading requirements from {requirements_file}...")
        lines = read_markdown(requirements_file)

        click.echo("Validating requirements file...")
        validate_requirements_command.callback(file_path=requirements_file)

        click.echo("Parsing Functional Requirements...")
        system_features_data = parse_lines(lines)

        system_features = {}
        for sf_obj in system_features_data:
            # Use sf_obj.description as the key for the system_features dictionary
            # The description from parse_lines already has the 'SR-X' removed and cleaned.
            system_features[sf_obj.description] = []
            for fr_obj in sf_obj.functional_requirements:
                system_features[sf_obj.description].append(
                    {"name": fr_obj.id, "description": fr_obj.description}
                )

        if not system_features:
            click.echo(
                "No System Features or Functional Requirements found in the file."
            )
            return

        click.echo("\n--- Found Functional Requirements ---")
        for sf_name, frs in system_features.items():
            click.echo(f"\nSystem Feature: {sf_name}")
            for fr in frs:
                click.echo(f"  - {fr['name']}: {fr['description']}")

        click.echo("\nStarting import process. You will be prompted for each FR.")

        for sf_name, frs in system_features.items():
            click.echo(
                f"\nProcessing Functional Requirements for System Feature: {sf_name}"
            )
            for fr in frs:
                prompt = f"Create FR '{fr['name']}' (Description: '{fr['description']}') under System Feature '{sf_name}'? (Y/n)"
                if not click.confirm(prompt):
                    click.echo("Import process cancelled by user.")
                    return

                click.echo(f"Creating FR '{fr['name']}'...")
                try:
                    create_fr.callback(
                        space_name="Everywhere",
                        fr_name=fr["name"],
                        fr_description=fr["description"],
                        fr_status="To Do",  # Default status
                        system_feature_id=None,  # Not using ID here
                        system_feature_name=sf_name,
                        system_feature_type_key="bafyreiczbkx2ungqnhdf6c7haiq3efjvpb3cqm5tyfnpei3nopbexf7o2e",  # Hardcoded SF type key
                        links=None,
                        template_id="bafyreidchi3wlbchypmpp3tksocuxzyh6hozuar4vihogm7jg7ps53yzby",  # Default template ID
                    )
                except Exception as e:
                    click.echo(f"Error creating FR '{fr['name']}': {e}")
                    import traceback

                    click.echo(traceback.format_exc())
                    return

        click.echo("\nImport process completed.")

    except FileNotFoundError:
        click.echo(f"Error: The file '{requirements_file}' was not found.")
    except click.exceptions.Abort:
        click.echo("\nImport process cancelled by user.")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
        import traceback

        click.echo(traceback.format_exc())
