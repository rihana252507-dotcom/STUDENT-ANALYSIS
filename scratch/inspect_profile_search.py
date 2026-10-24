with open('static/js/app.js', encoding='utf-8') as f:
    text = f.read()

idx = text.find('profileSearchInput')
print(text[idx-50:idx+1500])
