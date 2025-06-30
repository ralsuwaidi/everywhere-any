from dataclasses import dataclass, field
from typing import List

from anytype_api.client import AnytypeClient


@dataclass
class API:
    id: str
    space_id: str
    name: str = ""
    status: str = ""
    postman_url: str = ""
    api_type: str = ""

    def __post_init__(self):
        client = AnytypeClient()
        obj = client.get_object(self.space_id, self.id)["object"]
        self.name = obj.get("name", "Unknown API")
        for prop in obj.get("properties", []):
            if prop.get("name") == "Status":
                self.status = prop.get("select", {}).get("name", "")
            if prop.get("name") == "Postman URL":
                self.postman_url = prop.get("url", "")
            if prop.get("name") == "API Type":
                self.api_type = prop.get("select", {}).get("name", "")


@dataclass
class FunctionalRequirement:
    id: str
    space_id: str
    name: str = ""
    description: str = ""
    status: str = ""
    sort_key: List[int] = field(default_factory=list)
    apis: List[API] = field(default_factory=list)

    def __post_init__(self):
        client = AnytypeClient()
        obj = client.get_object(self.space_id, self.id)["object"]
        self.name = obj.get("name", "Unknown Functional Requirement")
        fr_name = obj.get("name", "")
        try:
            self.sort_key = [int(p) for p in fr_name.replace("FR-", "").split(".")]
        except ValueError:
            self.sort_key = [
                0,
                0,
            ]  # Default sort key for names that don't match the pattern
        for prop in obj.get("properties", []):
            if prop.get("key") == "description":
                self.description = prop.get("text", "")
            elif prop.get("key") == "status":
                self.status = prop.get("select", {}).get("name", "")


@dataclass
class SystemFeature:
    id: str
    space_id: str
    name: str = ""
    description: str = ""
    custom_id: str = ""
    functional_requirements: List[FunctionalRequirement] = field(default_factory=list)

    def __post_init__(self):
        client = AnytypeClient()
        obj = client.get_object(self.space_id, self.id)["object"]
        self.name = obj.get("name", "Unknown System Feature")
        for prop in obj.get("properties", []):
            if prop.get("key") == "description":
                self.description = prop.get("text", "")
            elif prop.get("key") == "6829bde80dd8772c7c96a582":
                self.custom_id = prop.get("text", "")
            elif prop.get("key") == "backlinks" and prop.get("objects"):
                # Filter out non-Functional Requirement objects before creating them
                fr_ids = []
                for linked_obj_id in prop.get("objects"):
                    linked_obj = client.get_object(self.space_id, linked_obj_id)[
                        "object"
                    ]
                    if (
                        linked_obj.get("type", {}).get("name")
                        == "Functional Requirement"
                    ):
                        fr_name = linked_obj.get("name", "")
                        if fr_name.startswith("FR-"):
                            try:
                                [int(p) for p in fr_name.replace("FR-", "").split(".")]
                                fr_ids.append(linked_obj_id)
                            except ValueError:
                                pass  # Ignore FRs that don't conform to the naming convention

                for fr_id in fr_ids:
                    self.functional_requirements.append(
                        FunctionalRequirement(id=fr_id, space_id=self.space_id)
                    )


@dataclass
class ReportData:
    system_features: List[SystemFeature] = field(default_factory=list)
