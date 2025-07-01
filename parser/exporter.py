import csv
import json

from .models import SystemFeature


def export_to_json(features: list[SystemFeature], filepath: str):
    def serialize(obj):
        if isinstance(obj, SystemFeature):
            return {
                "id": obj.id,
                "description": obj.description,
                "functional_requirements": [
                    serialize(fr) for fr in obj.functional_requirements
                ],
            }
        elif isinstance(obj, dict):
            return obj
        else:  # FunctionalRequirement
            return vars(obj)

    with open(filepath, "w") as f:
        json.dump([serialize(f) for f in features], f, indent=2)


def export_to_markdown(features: list[SystemFeature], filepath: str):
    with open(filepath, "w") as f:
        f.write("# System Features and Functional Requirements\n\n")
        for feature in features:
            f.write(f"## {feature.name}\n\n")
            f.write(f"**Description:** {feature.description}\n\n")
            f.write("### Functional Requirements:\n\n")
            for fr in feature.functional_requirements:
                f.write(f"- **{fr.name}**: {fr.description}\n")
            f.write("\n")

def export_to_markdown_table(features: list[SystemFeature], filepath: str):
    with open(filepath, "w") as f:
        f.write("| FR | Description | API | Status |\n")
        f.write("|---|---|---|---|\n")
        for sf in features:
            sf.functional_requirements.sort(key=lambda fr: fr.sort_key)
            for fr in sf.functional_requirements:
                if fr.apis:
                    for i, api in enumerate(fr.apis):
                        fr_name = fr.name if i == 0 else ""
                        fr_description = fr.description if i == 0 else ""
                        api_name = api.name
                        if api.postman_url:
                            api_name = f"[{api_name}]({api.postman_url})"
                        f.write(f"| {fr_name} | {fr_description} | {api_name} | {api.status} |\n")
                else:
                    f.write(f"| {fr.name} | {fr.description} | | {fr.status} |\n")

def export_to_csv(features: list[SystemFeature], filepath: str):
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FR", "Description", "API", "Status"])
        for sf in features:
            sf.functional_requirements.sort(key=lambda fr: fr.sort_key)
            for fr in sf.functional_requirements:
                if fr.apis:
                    for i, api in enumerate(fr.apis):
                        fr_name = fr.name if i == 0 else ""
                        fr_description = fr.description if i == 0 else ""
                        api_name = api.name
                        if api.postman_url:
                            api_name = f"[{api_name}]({api.postman_url})"
                        writer.writerow([fr_name, fr_description, api_name, api.status])
                else:
                    writer.writerow([fr.name, fr.description, "", fr.status])
