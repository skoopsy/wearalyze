def flatten_nested_dict(d: dict(), parent_key='', sep='_') -> dict():
    """
    Flattens a nested dictionary by giving the new keys names based on the
    nested dict keys

    Untested atm
    """
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)
