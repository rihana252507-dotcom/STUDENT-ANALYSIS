with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def student_dashboard')
idx_end = text.find('def ', idx+20)
print(text[idx_end-800:idx_end])
