with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\faculty_dashboard.html', 'r', encoding='utf-8') as f:
    fac_html = f.read()

pos = fac_html.find('id="simulatorModal"')
pos_end = fac_html.find('<!-- MODAL', pos + 20)
if pos_end == -1:
    pos_end = pos + 3000
print(fac_html[pos:pos_end])
