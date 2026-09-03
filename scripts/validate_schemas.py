import json
from pathlib import Path

if __name__ == "__main__":
    schema_dir = Path(__file__).resolve().parents[1] / "schemas"
    for path in sorted(schema_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as file_obj:
            json.load(file_obj)
    print("schemas_valid")
