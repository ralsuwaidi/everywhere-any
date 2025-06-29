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
    "--output-file",
    default="report.md",
    help="The name of the output Markdown file.",
)
def generate_report(space_name, output_file):
    """Generates a Markdown report of System Features and Functional Requirements from Anytype."""
    try:
        anytype_client = AnytypeClient()
        spaces = anytype_client.get_spaces()
        space = next((s for s in spaces["data"] if s["name"] == space_name), None)
        if not space:
            click.echo(f"Error: Space '{space_name}' not found.")
            return
        space_id = space["id"]

        report_content = []
        total_sfs = 0
        total_frs = 0

        # Fetch System Features
        sf_type_key = "bafyreiczbkx2ungqnhdf6c7haiq3efjvpb3cqm5tyfnpei3nopbexf7o2e" # Hardcoded SF type key
        system_features_results = anytype_client.search_objects(space_id, "", [sf_type_key])
        system_features = system_features_results["data"] if system_features_results and system_features_results["data"] else []
        total_sfs = len(system_features)

        # Fetch Functional Requirements
        fr_type_key = "6829be190dd8772c7c96a583" # Hardcoded FR type key
        functional_requirements_results = anytype_client.search_objects(space_id, "", [fr_type_key])
        functional_requirements = functional_requirements_results["data"] if functional_requirements_results and functional_requirements_results["data"] else []
        total_frs = len(functional_requirements)

        # Fetch API objects
        api_type_id = "bafyreicpin6mrj5btg3tqy6ve5twfjqittegdmojpai6d6vmhbuqmkmytq" # Hardcoded API type ID
        api_results = anytype_client.search_objects(space_id, "", [api_type_id])
        apis = api_results["data"] if api_results and api_results["data"] else []

        # Create a map for easy lookup of APIs by their ID
        apis_by_id = {api["id"]: api for api in apis}

        # Sort System Features by their custom 'Id' property numerically
        def get_sf_sort_key(sf_obj):
            for prop in sf_obj.get("properties", []):
                if prop.get("key") == "6829bde80dd8772c7c96a582": # Custom 'Id' property key
                    sf_id_str = prop.get("text", "").replace("SR-", "")
                    try:
                        return int(sf_id_str)
                    except ValueError:
                        return float('inf') # Handle cases where ID is not purely numeric
            return float('inf') # SFs without the custom ID go to the end

        system_features.sort(key=get_sf_sort_key)

        # Create a map for easy lookup of FRs by linked SF ID, and store parsed FR numbers for sorting
        frs_by_sf_id = {}
        # Create a map for easy lookup of APIs by linked FR ID
        apis_by_fr_id = {}

        for fr_obj in functional_requirements:
            linked_sf_id = None
            for prop in fr_obj.get("properties", []):
                if prop.get("key") == "6829c5d10dd8772c7c96a599" and prop.get("objects"):
                    linked_sf_id = prop["objects"][0] # Assuming one linked SF
                    break

            if linked_sf_id:
                if linked_sf_id not in frs_by_sf_id:
                    frs_by_sf_id[linked_sf_id] = []
                
                # Parse FR number for sorting (e.g., "FR-1.1" -> [1, 1])
                fr_name = fr_obj.get("name", "")
                fr_number_parts = [int(p) for p in fr_name.replace("FR-", "").split(".")]
                frs_by_sf_id[linked_sf_id].append({"obj": fr_obj, "sort_key": fr_number_parts})

        # Populate apis_by_fr_id map
        for api_obj in apis:
            linked_fr_ids = []
            for prop in api_obj.get("properties", []):
                if prop.get("key") == "6829e4c40dd8772c7c96a5ac" and prop.get("objects"):
                    linked_fr_ids.extend(prop["objects"])
            
            for fr_id in linked_fr_ids:
                if fr_id not in apis_by_fr_id:
                    apis_by_fr_id[fr_id] = []
                apis_by_fr_id[fr_id].append(api_obj)

        # Sort FRs within each SF group
        for sf_id in frs_by_sf_id:
            frs_by_sf_id[sf_id].sort(key=lambda x: x["sort_key"])

        # Summary Section
        report_content.append("# Requirements Report\n")
        report_content.append(f"## Summary\n")
        report_content.append(f"- Total System Features: {total_sfs}\n")
        report_content.append(f"- Total Functional Requirements: {total_frs}\n\n")

        # System Features and Functional Requirements Section
        report_content.append("## System Features and Functional Requirements\n")
        for sf_obj in system_features:
            sf_name = sf_obj.get("name", "Unknown System Feature")
            sf_description = ""
            sf_custom_id = ""
            for prop in sf_obj.get("properties", []):
                if prop.get("key") == "description":
                    sf_description = prop.get("text", "")
                elif prop.get("key") == "6829bde80dd8772c7c96a582": # Custom 'Id' property key
                    sf_custom_id = prop.get("text", "")
            
            # Use the custom 'Id' as the SR-X prefix
            report_content.append(f"### {sf_custom_id} {sf_name}\n")
            if sf_description:
                report_content.append(f"> {sf_description}\n")
            report_content.append(f"\n")

            # List associated Functional Requirements
            associated_frs_data = frs_by_sf_id.get(sf_obj["id"], [])
            if associated_frs_data:
                report_content.append(f"#### Functional Requirements\n")
                for fr_data in associated_frs_data:
                    fr_obj = fr_data["obj"]
                    fr_name = fr_obj.get("name", "Unknown Functional Requirement")
                    fr_description = ""
                    fr_status = ""
                    for prop in fr_obj.get("properties", []):
                        if prop.get("key") == "description":
                            fr_description = prop.get("text", "")
                        elif prop.get("key") == "status":
                            fr_status = prop.get("value", "")

                    fr_status = ""
                    for prop in fr_obj.get("properties", []):
                        if prop.get("key") == "description":
                            fr_description = prop.get("text", "")
                        elif prop.get("key") == "status":
                            fr_status = prop.get("select", {}).get("name", "")

                    if fr_status == "Done":
                        fr_name += " (Done)"
                    report_content.append(f"- **{fr_name}**: {fr_description}\n")

                    # Append linked APIs
                    linked_apis = apis_by_fr_id.get(fr_obj["id"], [])
                    if linked_apis:
                        report_content.append(f"  - **Linked APIs:**\n")
                        for api_obj in linked_apis:
                            api_name = api_obj.get("name", "Unknown API")
                            api_status = ""
                            for prop in api_obj.get("properties", []):
                                if prop.get("key") == "status":
                                    api_status = prop.get("select", {}).get("name", "")
                                    break
                            if api_status == "Done":
                                api_name += " (Done)"
                            report_content.append(f"    - {api_name}\n")
            else:
                report_content.append(f"_No Functional Requirements found for {sf_name}_\n")
            report_content.append("\n")

        # Write to file
        with open(output_file, "w") as f:
            f.writelines(report_content)

        click.echo(f"✅ Report generated successfully: {output_file}")

    except Exception as e:
        click.echo(f"Error generating report: {e}")
        import traceback
        click.echo(traceback.format_exc())