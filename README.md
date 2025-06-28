# Everywhere Any

`Everywhere Any` is a command-line tool designed to interact with Anytype, allowing you to parse requirements from markdown files, create objects in Anytype spaces, and list existing objects.

## Features

- **Parse Requirements**: Reads functional and system requirements from a markdown file (`requirements.md`).
- **Create Objects**: Creates SystemFeature and FunctionalRequirement objects in a specified Anytype space.
- **List Objects**: Lists objects in an Anytype space, with options to filter by type and search query.
- **List Functional Requirements**: Lists all Functional Requirements in a given space.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/everywhere-any.git
    cd everywhere-any
    ```
2.  **Install dependencies**:
    ```bash
    pip install -e .
    ```
    Or, if you are using `uv`:
    ```bash
    uv pip install -e .
    ```

## Configuration

Create a `.env` file in the root directory of the project with your Anytype API token:

```
ANYTYPE_API_TOKEN=your_anytype_api_token_here
```

## Usage

### General Command Structure

```bash
python main.py [COMMAND] --help
```

### Commands

#### `create`

Parse a requirements file and create objects in Anytype.

```bash
python main.py create --space-name "Your Space Name" --sf-type-key "page" --fr-type-key "task"
```

- `--space-name` (required): The name of the Anytype space.
- `--sf-type-key` (optional, default: `page`): The type key for SystemFeature objects.
- `--fr-type-key` (optional, default: `task`): The type key for FunctionalRequirement objects.

#### `list-objects`

List objects in an Anytype space. If `--type-keys` is not provided, it will prompt you to select object types interactively.

```bash
python main.py list-objects --space-name "Your Space Name" --query "search term" --type-keys "type1,type2"
```

- `--space-name` (optional, default: `Everywhere`): The name of the Anytype space.
- `--query` (optional, default: `""`): The search query.
- `--type-keys` (optional): A comma-separated list of type keys or names to search for.

#### `list-frs`

List all Functional Requirements in a given space.

```bash
python main.py list-frs --space-name "Your Space Name" --fr-type-key "task"
```

- `--space-name` (required, default: `Everywhere`): The name of the Anytype space.
- `--fr-type-key` (optional, default: `task`): The type key for FunctionalRequirement objects.

## Project Structure

- `main.py`: The main entry point for the CLI tool.
- `anytype_api/`: Contains the Anytype API client.
- `parser/`: Contains logic for parsing markdown, exporting to JSON, and generating statistics.
  - `exporter.py`: Handles exporting parsed data to JSON.
  - `models.py`: Defines data models for requirements.
  - `parser.py`: Parses markdown lines into requirement objects.
  - `reader.py`: Reads markdown files.
  - `stats.py`: Provides functions for printing statistics and validating requirements.
