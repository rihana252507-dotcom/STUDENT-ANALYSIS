with open('templates/faculty_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'studentDetailModal' in l or 'modalUpdateIntervention' in l:
        for j in range(i, min(len(lines), i+25)):
            print(f"{j+1}: {lines[j]}", end='')
        print("\n" + "="*50 + "\n")
