with open('templates/faculty_dashboard.html', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="studentDetailModal"')
if idx != -1:
    print("=== studentDetailModal in faculty_dashboard.html ===")
    print(text[idx:idx+3000])
else:
    print("studentDetailModal not found by id")
