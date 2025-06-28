import re


def print_stats(features):
    total_srs = len(features)
    total_frs = sum(len(sr.functional_requirements) for sr in features)

    print("\n📊 Statistics:")
    print(f"- Total System Features (SR): {total_srs}")
    print(f"- Total Functional Requirements (FR): {total_frs}\n")

    for sr in features:
        fr_count = len(sr.functional_requirements)
        last_frs = sr.functional_requirements[-1:] if fr_count else []
        short_desc = sr.description.split(".")[0].strip()
        print(f"{sr.id} ({fr_count} FRs) - {short_desc}...")

        for fr in last_frs:
            print(f"   ↳ Last FR: {fr.id} - {fr.description[:60]}...")

    print("-" * 40)


def validate_frs(features, md_text):
    total_frs = sum(len(sr.functional_requirements) for sr in features)

    fr_pattern = re.compile(r"\bFR-(\d+(?:\.\d+)+)(?=\b|[^.\d])")
    fr_ids_in_md = set(f"FR-{match}" for match in fr_pattern.findall(md_text))

    fr_ids_in_json = set()
    for sr in features:
        for fr in sr.functional_requirements:
            fr_ids_in_json.add(fr.id)

    if len(fr_ids_in_md) != total_frs or fr_ids_in_md != fr_ids_in_json:
        print(f"\n⚠️  WARNING: Mismatch in FR count or content!")
        print(f"- FRs detected by regex in markdown: {len(fr_ids_in_md)}")
        print(f"- FRs parsed into JSON: {total_frs}")

        missing_in_json = fr_ids_in_md - fr_ids_in_json
        if missing_in_json:
            print(f"- FRs missing from parsed JSON ({len(missing_in_json)}):")
            for fr_id in sorted(missing_in_json):
                print(f"  - {fr_id}")

        extra_in_json = fr_ids_in_json - fr_ids_in_md
        if extra_in_json:
            print(
                f"- Extra FRs in JSON not detected in markdown ({len(extra_in_json)}):"
            )
            for fr_id in sorted(extra_in_json):
                print(f"  - {fr_id}")
