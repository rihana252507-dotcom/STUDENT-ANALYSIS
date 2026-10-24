with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Line 196 context:")
for i in range(190, 202):
    print(f"{i+1}: {lines[i]}", end='')

print("\nLine 437 context:")
for i in range(432, 444):
    print(f"{i+1}: {lines[i]}", end='')
