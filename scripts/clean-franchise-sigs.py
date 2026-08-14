"""Strip the redundant '<name> style' prefix from franchise signatures."""
import pathlib
import re

p = pathlib.Path("src/invokeai_mcp/franchises.py")
lines = p.read_text(encoding="utf-8").splitlines()
pattern = re.compile(r'(\s*\(\s*"[^"]+"\s*,\s*"[^"]+"\s*,\s*")(.*?)("\s*\),\s*$)')
out = []
count = 0
for line in lines:
    m = pattern.match(line)
    if m:
        sig = m.group(2)
        parts = sig.split(", ", 1)
        if len(parts) == 2 and parts[0].endswith(" style"):
            line = m.group(1) + parts[1] + m.group(3)
            count += 1
    out.append(line)
p.write_text("\n".join(out), encoding="utf-8")
print(f"cleaned {count} signatures")
