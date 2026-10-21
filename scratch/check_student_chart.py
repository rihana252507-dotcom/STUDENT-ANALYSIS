with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    stu_html = f.read()

pos = stu_html.find('id="section-my-success-score"')
pos_end = stu_html.find('</section>', pos)
print("Length of section-my-success-score:", pos_end - pos)
print("Canvas in section:", 'canvas' in stu_html[pos:pos_end].lower())
