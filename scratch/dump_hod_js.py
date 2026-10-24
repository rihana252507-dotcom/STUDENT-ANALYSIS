import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

scripts = re.findall(r"<script[\s\S]*?</script>", content)
if len(scripts) >= 2:
    out_path = os.path.join(os.path.dirname(__file__), "hod_script.js")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write(scripts[1])
    print("Wrote hod_script.js (utf-8)")
