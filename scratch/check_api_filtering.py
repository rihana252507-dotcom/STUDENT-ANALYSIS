with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- /api/students (lines 520-565) ---")
for i in range(519, 565):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- /api/students/<student_id> (lines 659-685) ---")
for i in range(658, 685):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- /api/interventions (lines 1060-1090) ---")
for i in range(1059, 1090):
    print(f"{i+1}: {lines[i]}", end='')
