with open('templates/login.html', 'r', encoding='utf-8') as f:
    text = f.read()

f_idx = text.find('<form')
if f_idx != -1:
    print('Form tag:')
    print(text[f_idx:f_idx+500])

s_idx = text.rfind('<script')
if s_idx != -1:
    print('Script tag:')
    print(text[s_idx:])
