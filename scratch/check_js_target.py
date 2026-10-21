import re

JS_PATH = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js"

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# Let's inspect where renderRiskWatchlist is defined
pos = js.find("function renderRiskWatchlist(students)")
assert pos != -1, "renderRiskWatchlist not found"

end_func_pos = js.find("}\r\n\r\n// Faculty Risk Alerts Table", pos)
if end_func_pos == -1:
    end_func_pos = js.find("}\n\n// Faculty Risk Alerts Table", pos)
if end_func_pos == -1:
    end_func_pos = js.find("// Faculty Risk Alerts Table", pos)

print("Found renderRiskWatchlist. pos:", pos, "end_pos:", end_func_pos)
