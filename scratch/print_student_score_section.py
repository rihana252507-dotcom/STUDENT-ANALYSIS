with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html', 'r', encoding='utf-8') as f:
    txt = f.read()

pos = txt.find('id="section-my-success-score"')
pos_end = txt.find('</section>', pos)
print("=== section-my-success-score ===")
print(txt[pos:pos_end+10])
