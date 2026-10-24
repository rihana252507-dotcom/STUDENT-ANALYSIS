with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'/api/[a-zA-Z0-9_\/]*setting[a-zA-Z0-9_\/]*', text, re.IGNORECASE)
print("Settings API in app.py:", matches)

matches_config = re.findall(r'/api/[a-zA-Z0-9_\/]*config[a-zA-Z0-9_\/]*', text, re.IGNORECASE)
print("Config API in app.py:", matches_config)
