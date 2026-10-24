with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1145, 1175):
    print(f"{i+1}: {lines[i]}", end='')
