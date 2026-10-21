import os, glob

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.html', '.js', '.py')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'low risk' in content.lower() or 'attendance students' in content.lower() or 'attendance' in content.lower() and 'students' in content.lower():
                        matches = []
                        for i, line in enumerate(content.splitlines()):
                            if 'low risk' in line.lower() or 'attendance students' in line.lower() or 'attendance' in line.lower() and 'students' in line.lower():
                                matches.append(f"{i+1}: {line.strip()[:100]}")
                        if matches:
                            print(f"=== {path} ===")
                            for m in matches[:10]:
                                print(m)
            except Exception as e:
                pass
