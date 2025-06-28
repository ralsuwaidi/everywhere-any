import re

from .models import FunctionalRequirement, SystemFeature

sr_heading_pattern = re.compile(r"^###\s+(\d+\.\d+)\s+(.+)")
description_pattern = re.compile(r"^\*\*\s*Description:\s*(.+)")
stimulus_pattern = re.compile(r"^\*\*\s*Stimulus/Response Sequences:\s*")
fr_pattern = re.compile(r"^[*-]\s*FR-(\d+\.\d+)(?:\*\*\:\*\*|:)\s*(.+)")
non_functional_pattern = re.compile(
    r"^##\s+3\.0\s+Non-Functional Requirements", re.IGNORECASE
)


def parse_lines(lines: list[str]) -> list[SystemFeature]:
    features = []
    current_sr = None
    collecting_description = False
    collecting_stimulus = False
    stimulus_lines = []
    parsing = True

    for line in lines:
        if non_functional_pattern.match(line):
            parsing = False
            continue

        if not parsing:
            continue

        sr_match = sr_heading_pattern.match(line)
        description_match = description_pattern.match(line)
        stimulus_match = stimulus_pattern.match(line)
        fr_match = fr_pattern.match(line)

        if sr_match:
            sr_number = sr_match.group(1)
            sr_desc = sr_match.group(2)

            if sr_number.startswith("2."):
                sr_id = f"SR-{sr_number.split('.')[1]}"
                current_sr = SystemFeature(id=sr_id, description=sr_desc)
                features.append(current_sr)
                collecting_description = True
                collecting_stimulus = False
                stimulus_lines = []
            else:
                current_sr = None
            continue

        if collecting_description and description_match and current_sr:
            current_sr.description = description_match.group(1)
            collecting_description = False
            collecting_stimulus = True
            continue

        if collecting_stimulus and stimulus_match:
            stimulus_lines = []
            continue

        if (
            collecting_stimulus
            and (line.strip().startswith("*") or line.strip().startswith("-"))
            and not fr_match
        ):
            stimulus_lines.append(line.lstrip("*- ").strip())
            current_sr.description += " Stimulus/Response: " + " ".join(stimulus_lines)
            continue

        if fr_match and current_sr:
            fr_number = fr_match.group(1)
            fr_desc = fr_match.group(2)
            fr_id = f"FR-{fr_number}"
            fr_obj = FunctionalRequirement(
                id=fr_id,
                linked_sr=current_sr.id,
                completion_state="To Do",
                description=fr_desc,
            )
            current_sr.functional_requirements.append(fr_obj)

    return features
