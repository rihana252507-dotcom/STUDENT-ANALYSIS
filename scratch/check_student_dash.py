with open('templates/student_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(415, 460):
    print(f"{i+1}: {lines[i].rstrip()}")
