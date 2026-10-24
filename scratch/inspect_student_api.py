with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@app.route("/api/students/<student_id>"')
print("=== /api/students/<student_id> in app.py ===")
print(text[idx:idx+2500])
