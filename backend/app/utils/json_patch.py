from __future__ import annotations
from typing import Any, List, Tuple


def _unescape(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def _split_ptr(path: str) -> List[str]:
    if not path:
        return []
    if not path.startswith("/"):
        raise ValueError(f"Invalid JSON Pointer: {path}")
    return [_unescape(p) for p in path.split("/")[1:]]


def _traverse(doc: Any, parts: List[str]) -> Tuple[Any, str]:
    if not parts:
        raise ValueError("Pointer must not reference the whole document for write ops")
    cur = doc
    for key in parts[:-1]:
        if isinstance(cur, list):
            idx = int(key)
            cur = cur[idx]
        else:
            cur = cur[key]
    return cur, parts[-1]


def apply_patch(doc: Any, patch: List[dict], allowed_prefix: str | None = None) -> Any:
    import copy
    out = copy.deepcopy(doc)
    for op in patch:
        operation = op["op"]
        path = op["path"]
        if allowed_prefix is not None and not path.startswith(allowed_prefix):
            raise ValueError(f"Patch path {path} not allowed; must start with {allowed_prefix}")
        parts = _split_ptr(path)
        parent, last = _traverse(out, parts)

        if operation == "remove":
            if isinstance(parent, list):
                idx = int(last)
                parent.pop(idx)
            else:
                del parent[last]
        elif operation in ("add", "replace"):
            value = op.get("value")
            if isinstance(parent, list):
                if last == "-":
                    parent.append(value)
                else:
                    idx = int(last)
                    if operation == "replace":
                        parent[idx] = value
                    else:
                        parent.insert(idx, value)
            else:
                parent[last] = value
        else:
            raise ValueError(f"Unsupported op: {operation}")
    return out

