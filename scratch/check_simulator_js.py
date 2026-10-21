with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

pos = js.find('populateSimulatorDropdown')
print("=== populateSimulatorDropdown in app.js ===")
print(js[pos:pos+1500])

pos2 = js.find('btnRunSimulation')
print("\n=== btnRunSimulation in app.js ===")
print(js[pos2-100:pos2+1500])
