def split_name(name: str):
    """Turn CamelCase into ["camel", "case"] and snake_case into ["snake", "case"]"""
    parts = [part for part in name.split("_") if part != ""]
    return [subpart for part in parts for subpart in split_camel_case(part)]


def split_camel_case(name: str):
    boundaries = [
        idx
        for idx in range(len(name) + 1)
        if (
            idx == 0
            or idx == len(name)
            or (name[idx - 1].islower() and name[idx].isupper())
            or (
                idx + 1 < len(name)
                and name[idx - 1].isupper()
                and name[idx].isupper()
                and name[idx + 1].islower()
            )
        )
    ]
    return [
        name[start:end].lower() for start, end in zip(boundaries[:-1], boundaries[1:])
    ]
