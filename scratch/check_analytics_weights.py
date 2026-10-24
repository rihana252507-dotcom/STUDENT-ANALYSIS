with open('services/analytics.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('weights')
if idx != -1:
    print(text[max(0, idx-100):min(len(text), idx+300)])
else:
    print("No 'weights' in services/analytics.py")
