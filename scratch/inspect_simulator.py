with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

pos = admin_html.find('id="simulatorModal"')
if pos != -1:
    print("=== simulatorModal in admin_dashboard.html ===")
    print(admin_html[pos:pos+3500])

with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    student_html = f.read()

pos2 = student_html.find('What-If Simulator')
if pos2 != -1:
    print("\n=== What-If Simulator in student_dashboard.html ===")
    print(student_html[pos2:pos2+3500])
