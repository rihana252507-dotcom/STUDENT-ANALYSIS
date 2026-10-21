with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.finditer(r'<section id="([^"]+)"', text)
indices = [m.start() for m in matches]
indices.append(len(text))

for i in range(len(indices)-1):
    sec_content = text[indices[i]:indices[i+1]]
    sec_id = re.search(r'<section id="([^"]+)"', sec_content).group(1)
    print(f"\n=================== SECTION {sec_id} ===================")
    for line in sec_content.splitlines()[:15]:
        print(line[:100])
