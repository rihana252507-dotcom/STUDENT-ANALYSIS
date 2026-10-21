with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\frontend\index.html', 'r', encoding='utf-8') as f:
    f_html = f.read()

pos = f_html.find('simulator')
while pos != -1:
    print("Match at pos:", pos)
    print(f_html[pos-100:pos+300])
    print("-" * 40)
    pos = f_html.find('simulator', pos+20)
