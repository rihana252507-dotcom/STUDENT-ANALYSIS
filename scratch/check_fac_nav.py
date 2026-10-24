with open('templates/faculty_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(35, 110):
    print(f"{i+1}: {lines[i]}", end='')
