with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    stu_html = f.read()

pos = stu_html.find('id="section-my-success-score"')
pos_end = stu_html.find('</section>', pos)
print(stu_html[pos+2500:pos_end])
