with open('static/css/style.css', encoding='utf-8') as f:
    css = f.read()

idx = css.find('.text-gradient-purple')
if idx != -1:
    print(css[idx:idx+300])
else:
    print("text-gradient-purple not found in style.css")
