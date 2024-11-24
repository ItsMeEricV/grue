import uuid


# check if an input string is a valid UUID4 string
def uuid_validate(uuid_str: str) -> uuid.UUID | None:
    try:
        return uuid.UUID(uuid_str, version=4)
    except ValueError:
        return None
