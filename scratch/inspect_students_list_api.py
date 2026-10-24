with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@app.route("/api/students", methods=["GET"])')
print("=== /api/students ===")
print(text[idx:idx+2500])
