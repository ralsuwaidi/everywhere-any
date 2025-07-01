from parser.models import API, SystemFeature
from parser.exporter import export_to_markdown_table, export_to_csv

import click
import markdown
from dotenv import load_dotenv
from weasyprint import HTML
import os

from anytype_api.client import AnytypeClient

load_dotenv()


@click.command()
@click.option(
    "--space-name",
    default="Everywhere",
    help="The name of the Anytype space.",
)
@click.option(
    "--output-file",
    default="report",
    help="The name of the output file (without extension).",
)
@click.option(
    "--output-format",
    type=click.Choice(["md", "pdf", "md-table", "csv"], case_sensitive=False),
    default="md",
    help="The output format for the report.",
)
def generate_report(space_name, output_file, output_format):
    """Generates a Markdown report of System Features and Functional Requirements from Anytype."""
    try:
        # Create reports directory if it doesn't exist
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)

        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        # Fetch System Features
        sf_type_key = "bafyreiczbkx2ungqnhdf6c7haiq3efjvpb3cqm5tyfnpei3nopbexf7o2e"  # Hardcoded SF type key
        system_features_results = anytype_client.search_objects(
            space_id, "", [sf_type_key]
        )
        system_feature_ids = [
            obj["id"] for obj in system_features_results.get("data", [])
        ]

        system_features = [
            SystemFeature(id=sf_id, space_id=space_id) for sf_id in system_feature_ids
        ]

        # Fetch API objects and create a mapping for easy lookup
        api_type_id = "bafyreicpin6mrj5btg3tqy6ve5twfjqittegdmojpai6d6vmhbuqmkmytq"  # Hardcoded API type ID
        api_results = anytype_client.search_objects(space_id, "", [api_type_id])
        apis_by_fr_id = {}
        for api_obj_data in api_results.get("data", []):
            api_obj = API(id=api_obj_data["id"], space_id=space_id)
            for prop in api_obj_data.get("properties", []):
                if prop.get("key") == "6829e4c40dd8772c7c96a5ac" and prop.get(
                    "objects"
                ):
                    for fr_id in prop.get("objects"):
                        if fr_id not in apis_by_fr_id:
                            apis_by_fr_id[fr_id] = []
                        apis_by_fr_id[fr_id].append(api_obj)

        # Sort System Features by their custom 'Id' property numerically
        def get_sf_sort_key(sf_obj):
            sf_id_str = sf_obj.custom_id.replace("SR-", "")
            try:
                return int(sf_id_str)
            except ValueError:
                return float("inf")

        system_features.sort(key=get_sf_sort_key)

        # Populate FRs and APIs
        for sf in system_features:
            for fr in sf.functional_requirements:
                fr.apis = apis_by_fr_id.get(fr.id, [])

        if output_format == "md-table":
            final_output_file = os.path.join(reports_dir, f"{output_file}.md")
            export_to_markdown_table(system_features, final_output_file)
            click.echo(f"✅ Report generated successfully: {final_output_file}")
            return
        if output_format == "csv":
            final_output_file = os.path.join(reports_dir, f"{output_file}.csv")
            export_to_csv(system_features, final_output_file)
            click.echo(f"✅ Report generated successfully: {final_output_file}")
            return

        report_content = []
        total_sfs = len(system_features)
        total_frs = sum(len(sf.functional_requirements) for sf in system_features)

        report_content.append("# Requirements Report\n")
        report_content.append(f"## Summary\n")
        report_content.append(f"- Total System Features: {total_sfs}\n")
        report_content.append(f"- Total Functional Requirements: {total_frs}\n\n")

        # System Features and Functional Requirements Section
        report_content.append("## System Features and Functional Requirements\n")
        for sf in system_features:
            sf.functional_requirements.sort(key=lambda fr: fr.sort_key)
            report_content.append(f"### {sf.custom_id} {sf.name}\n")
            if sf.description:
                report_content.append(f"> {sf.description}\n")
            report_content.append(f"\n")

            # List associated Functional Requirements
            if sf.functional_requirements:
                report_content.append(f"#### Functional Requirements\n")
                for fr in sf.functional_requirements:
                    fr_name = fr.name
                    if fr.status == "Done":
                        fr_name += " (Done)"
                    report_content.append(f"- **{fr_name}**: {fr.description}\n")

                    # Append linked APIs
                    if fr.apis:
                        report_content.append(f"  - **Linked APIs:**\n")
                        for api in fr.apis:
                            name_with_status = api.name
                            if api.status == "Done":
                                name_with_status += " (Done)"

                            if api.postman_url:
                                display_name = f"{api.api_type or ''} [{name_with_status}]({api.postman_url})"
                            else:
                                display_name = (
                                    f"{api.api_type or ''} {name_with_status}"
                                )

                            report_content.append(f"    - {display_name.strip()}\n")
            else:
                report_content.append(
                    f"_No Functional Requirements found for {sf.name}_\n"
                )
            report_content.append("\n")

        # Write to file
        if output_format == "md":
            final_output_file = os.path.join(reports_dir, f"{output_file}.md")
            with open(final_output_file, "w") as f:
                f.writelines(report_content)
            click.echo(f"✅ Report generated successfully: {final_output_file}")
        elif output_format == "pdf":
            final_output_file = os.path.join(reports_dir, f"{output_file}.pdf")
            md_content = "".join(report_content)

            click.echo(f"Converting Markdown to PDF: {final_output_file}...")

            try:
                html_content = markdown.markdown(md_content)
                HTML(string=html_content).write_pdf(final_output_file)
                click.echo(f"✅ Report generated successfully: {final_output_file}")
            except Exception as e:
                click.echo(f"Error during PDF conversion: {e}")

    except FileNotFoundError:
        click.echo(
            f"Error: The file '{output_file}.md' was not found during PDF conversion."
        )
    except click.exceptions.Abort:
        click.echo("\nReport generation cancelled by user.")
    except Exception as e:
        click.echo(f"Error generating report: {e}")
        import traceback

        click.echo(traceback.format_exc())
