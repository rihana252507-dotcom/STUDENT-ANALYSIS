with open('templates/faculty_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Faculty line 180 context:")
for i in range(175, 185):
    print(f"{i+1}: {lines[i]}", end='')

print("\nFaculty line 357 context:")
for i in range(352, 362):
    print(f"{i+1}: {lines[i]}", end='')

print("\nFaculty line 605 context:")
for i in range(600, 615):
    print(f"{i+1}: {lines[i]}", end='')
