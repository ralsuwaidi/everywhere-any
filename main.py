from parser.exporter import export_to_json
from parser.parser import parse_lines
from parser.reader import read_markdown
from parser.stats import print_stats, validate_frs

# Read and parse markdown
lines = read_markdown("requirements.md")
features = parse_lines(lines)

# Output JSON
export_to_json(features, "requirements.json")
print("✅ Requirements exported to requirements.json")

# Print stats
print_stats(features)

# Validate FR count
with open("requirements.md", "r") as f:
    md_text = f.read()

validate_frs(features, md_text)
