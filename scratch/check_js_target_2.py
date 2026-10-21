JS_PATH = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js"

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

pos = 39220
end_pos = 40869
print(js[pos:end_pos+40])
