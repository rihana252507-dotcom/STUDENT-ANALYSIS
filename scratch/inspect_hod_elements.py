import os
import re

path = os.path.join(os.path.dirname(__file__), "..", "templates", "hod_dashboard.html")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Check all script tags and css tags
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', content)
print("External scripts in hod_dashboard.html:", scripts)

links = re.findall(r'<link[^>]*href=["\']([^"\']+)["\']', content)
print("Stylesheets in hod_dashboard.html:", links)

# Check all canvas elements
canvases = re.findall(r'<canvas[^>]*id=["\']([^"\']+)["\']', content)
print("Canvas IDs:", canvases)

# Check all button elements and their onclick or IDs
buttons = re.findall(r'<button[^>]*>', content)
print(f"Total buttons in hod_dashboard.html: {len(buttons)}")
for b in buttons[:20]:
    print(b)

# Check all export buttons/links
exports = re.findall(r'<a[^>]*export[^>]*>|<button[^>]*export[^>]*>', content, re.IGNORECASE)
print("Export elements:", exports)

# Check all anchors
anchors = re.findall(r'<a[^>]*href=["\']([^"\']+)["\']', content)
print("Anchor hrefs:", set(anchors))
