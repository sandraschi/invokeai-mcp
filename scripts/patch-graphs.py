"""Patch graphs.py: flatten node data (v6 flat node fields)."""
import pathlib

p = pathlib.Path("src/invokeai_mcp/graphs.py")
c = p.read_text(encoding="utf-8")

old = '    def add(node: dict[str, Any]) -> str:\n        nid = node["id"]\n        nodes[nid] = node\n        return nid'
new = (
    '    def add(node: dict[str, Any]) -> str:\n'
    '        """Register a node. v6 uses FLAT node fields - data is merged in."""\n'
    '        nid = node["id"]\n'
    '        flat = {"id": nid, "type": node["type"]}\n'
    '        flat.update(node.get("data") or {})\n'
    '        nodes[nid] = flat\n'
    "        return nid\n"
)
count = c.count(old)
c = c.replace(old, new)
p.write_text(c, encoding="utf-8")
print("patched add() occurrences:", count)
