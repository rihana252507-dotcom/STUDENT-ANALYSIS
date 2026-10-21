with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    student_html = f.read()

pos = student_html.find('id="section-simulator"')
if pos != -1:
    print("=== section-simulator in student_dashboard.html ===")
    print(student_html[pos:pos+4000])
else:
    pos2 = student_html.find('Interactive What-If Simulator')
    if pos2 != -1:
        print("=== Interactive What-If Simulator in student_dashboard.html ===")
        print(student_html[pos2-200:pos2+4000])
