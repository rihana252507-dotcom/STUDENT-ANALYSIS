for file in ['templates/student_dashboard.html', 'templates/admin_dashboard.html', 'templates/faculty_dashboard.html']:
    with open(file, 'r', encoding='utf-8') as f:
        txt = f.read()
    import re
    links = re.findall(r'<a [^>]*simulator[^>]*>[^<]*</a>', txt, re.IGNORECASE)
    print(f"Links in {file}:", links)
    btns = re.findall(r'<button [^>]*simulator[^>]*>.*?</button>', txt, re.IGNORECASE | re.DOTALL)
    print(f"Buttons in {file}:", [b[:60] for b in btns])
