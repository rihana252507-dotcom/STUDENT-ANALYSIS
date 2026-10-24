with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Query academic_records')
print(repr(text[idx-20:idx+400]))
