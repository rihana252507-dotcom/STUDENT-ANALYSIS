with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def student_dashboard')
print("=== student_dashboard in app.py ===")
print(text[idx:idx+2500])
