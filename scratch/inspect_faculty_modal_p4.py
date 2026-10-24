with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="studentDetailModal"')
print(text[idx+5500:idx+8500])
