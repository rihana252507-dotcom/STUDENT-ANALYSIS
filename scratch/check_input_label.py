with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\css\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

pos = css.find('.input-group-custom')
print(css[pos:pos+400])
