import yaml

def load_schema_yaml(path):
    """
    Loads a schema YAML file and returns a Python dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def schema_to_description(schema_dict):
    parts = []
    tables = schema_dict.get("tables", [])

    for table in tables:
        tname = table.get("name")
        cols = []
        for col in table.get("columns", []):
            name = col.get("name")
            typ = col.get("type", "TEXT").upper()

            extras = []
            if col.get("pk"):
                extras.append("PK")
            if col.get("fk"):
                extras.append(f"FK->{col.get('fk')}")

            extras_txt = f" ({', '.join(extras)})" if extras else ""
            cols.append(f"{name} {typ}{extras_txt}")

        parts.append(f"Table {tname}: {', '.join(cols)}")

    return "\n".join(parts)

def load_schema(path):
    """Loads schema YAML and returns a description string."""
    return schema_to_description(load_schema_yaml(path))
