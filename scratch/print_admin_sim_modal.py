with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

pos = admin_html.find('id="simulatorModal"')
pos_end = admin_html.find('<!-- MODAL', pos + 20)
if pos_end == -1:
    pos_end = admin_html.find('</section>', pos)
if pos_end == -1:
    pos_end = pos + 4000

print("=== simulatorModal in admin_dashboard.html ===")
print(admin_html[pos:pos_end])
