with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\css\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

pos = css.find('.glass-modal-header')
print("=== .glass-modal-header in style.css ===")
print(css[pos:pos+300])
