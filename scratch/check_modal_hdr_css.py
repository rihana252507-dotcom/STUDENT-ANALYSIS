with open('static/css/style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'glass-modal-header' in l:
        for j in range(max(0, i-2), min(len(lines), i+20)):
            print(f"{j+1}: {lines[j]}", end='')
        break
