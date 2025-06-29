import click
from dotenv import load_dotenv

from parser.exporter import export_to_json
from parser.parser import parse_lines
from parser.reader import read_markdown
from parser.stats import print_stats, validate_frs

load_dotenv()


@click.command("validate")
@click.option(
    "--file-path",
    default="requirements.md",
    help="The path to the requirements markdown file.",
)
def validate_requirements_command(file_path: str):
    """Parses and validates a requirements markdown file."""
    lines = read_markdown(file_path)
    features = parse_lines(lines)

    export_to_json(features, "requirements.json")
    click.echo("✅ Requirements exported to requirements.json")

    print_stats(features)

    with open(file_path, "r") as f:
        md_text = f.read()
    validate_frs(features, md_text)
