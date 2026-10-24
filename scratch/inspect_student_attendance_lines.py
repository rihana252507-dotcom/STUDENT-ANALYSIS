with open('templates/student_dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'id="section-attendance"' in l:
        for j in range(i-1, min(len(lines), i+120)):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
