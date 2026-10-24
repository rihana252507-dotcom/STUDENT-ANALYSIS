with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('def get_student_academic_records')
if idx != -1:
    print(text[idx:idx+600])
