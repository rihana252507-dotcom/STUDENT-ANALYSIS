with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

pos = admin_html.find('id="simulatorModal"')
pos_end = admin_html.find('</div>\n    </div>\n  </div>', pos)
if pos_end == -1:
    pos_end = admin_html.find('<!-- MODAL 5', pos)
print("=== Admin simulatorModal ===")
print(admin_html[pos:pos_end+30])

with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\faculty_dashboard.html', 'r', encoding='utf-8') as f:
    fac_html = f.read()

pos = fac_html.find('id="simulatorModal"')
pos_end = fac_html.find('<!-- MODAL', pos + 20)
if pos_end == -1:
    pos_end = fac_html.find('</section>', pos)
print("\n=== Faculty simulatorModal ===")
print(fac_html[pos:pos+3000])

with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    stu_html = f.read()

pos = stu_html.find('Interactive What-If Simulator')
print("\n=== Student Simulator Section ===")
print(stu_html[pos-100:pos+2500])
