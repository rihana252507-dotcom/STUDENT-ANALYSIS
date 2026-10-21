with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
matches = [m.start() for m in re.finditer(r'function runScenarioSimulation', js)]
print("runScenarioSimulation matches:", matches)
if matches:
    print(js[matches[0]:matches[0]+2000])

matches2 = [m.start() for m in re.finditer(r'function populateSimulatorDropdown', js)]
print("\npopulateSimulatorDropdown matches:", matches2)
if matches2:
    print(js[matches2[0]:matches2[0]+1500])
