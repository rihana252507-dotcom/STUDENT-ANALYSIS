with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'section-interventions' in l:
        print(f'Start interventions: line {i}')
    if '</main>' in l:
        print(f'End of main: line {i}')
