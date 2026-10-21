with open(r'c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
matches = re.findall(r'.{0,50}(?:personalProjectedScore|personalDeltaText|simDeltaHighlight|simRecommendationText|simProjectedScore|simCurrentScore).{0,50}', js)
for m in matches:
    print(m.strip())
