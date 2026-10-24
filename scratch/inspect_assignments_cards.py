with open('templates/student_dashboard.html', encoding='utf-8') as f:
    lines = f.readlines()

for j in range(1225, 1255):
    print(f"{j+1}: {lines[j].rstrip()}")
