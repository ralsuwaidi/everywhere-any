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
