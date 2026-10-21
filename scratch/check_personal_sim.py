with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('function initPersonalSimulator')
print("=== initPersonalSimulator in app.js ===")
print(js[pos:pos+2000])
