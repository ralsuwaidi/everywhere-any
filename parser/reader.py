def read_markdown(filepath: str) -> list[str]:
    with open(filepath, "r") as file:
        return [line.strip() for line in file.readlines()]
