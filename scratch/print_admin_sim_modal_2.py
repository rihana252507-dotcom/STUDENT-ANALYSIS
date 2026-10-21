with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

pos = admin_html.find('id="simulatorModal"')
print(admin_html[pos+2500:pos+4500])
