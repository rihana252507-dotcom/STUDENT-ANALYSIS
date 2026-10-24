with open('app.py', encoding='utf-8') as f:
    text = f.read()

idx = text.find('sort_by = request.args.get("sort_by"')
print(text[idx-50:idx+800])
