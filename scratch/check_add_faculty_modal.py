with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1418, 1482):
    print(f"{i+1}: {lines[i]}", end='')
