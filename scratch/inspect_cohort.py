import sys

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(180, 215):
    print(f"{i+1}: {lines[i].rstrip()}")
