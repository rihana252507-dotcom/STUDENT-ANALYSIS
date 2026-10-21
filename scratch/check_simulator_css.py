with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\css\style.css', 'r', encoding='utf-8') as f:
    css = f.read()

keywords = ['glass-modal-card', 'glass-modal-overlay', 'cyber-select', 'simulator', 'glass-card']
for kw in keywords:
    pos = 0
    print(f"\n================ Keyword: {kw} ================")
    while True:
        idx = css.find(kw, pos)
        if idx == -1:
            break
        print(css[max(0, idx-50):min(len(css), idx+250)])
        print("-" * 30)
        pos = idx + len(kw) + 50
