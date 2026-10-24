with open('templates/hod_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Look for sidebar click handler
idx = text.find('sidebar-nav-link')
if idx != -1:
    print('Found sidebar-nav-link usage in JS or HTML')
# Find script block
s_idx = text.rfind('<script>')
if s_idx != -1:
    print(text[s_idx:s_idx+1500])
