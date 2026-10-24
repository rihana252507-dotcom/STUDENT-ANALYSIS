with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@app.route("/api/students/<student_id>"')
print(text[idx+2000:idx+4500])
