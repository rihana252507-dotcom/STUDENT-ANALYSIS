with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@app.route("/api/export/csv"')
idx2 = text.find('@app.route("/api/admin/faculty"', idx)
print("From /api/export/csv to next route:")
print(text[idx:idx2])
