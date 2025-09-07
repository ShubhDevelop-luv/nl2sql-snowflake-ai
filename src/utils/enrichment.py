def apply_edit_semantics(current: dict, patch: dict) -> dict:
    action = patch.get("action")
    key_values = {k: set(v) if isinstance(v, list) else v for k, v in patch.items() if k != "action"}

    if action == "add":
        for k, vals in key_values.items():
            current.setdefault(k, set()).update(vals)
    elif action in ("narrow", "only", "switch"):
        for k, vals in key_values.items():
            current[k] = set(vals)
    elif action == "remove":
        for k, vals in key_values.items():
            current[k] = set(current.get(k, set())) - set(vals)
    elif action == "reset":
        current.clear()
    return current
