with open('templates/faculty_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Line 820 in faculty_dashboard.html:")
for i in range(810, 830):
    print(f"{i+1}: {lines[i]}", end='')

print("\nLine 958 in faculty_dashboard.html:")
for i in range(950, 970):
    print(f"{i+1}: {lines[i]}", end='')
