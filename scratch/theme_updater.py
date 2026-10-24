def update_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"[{path}] Replaced: {old[:30]}... -> {new[:30]}...")

    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{path}] Saved.")

update_file(
    r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\js\app.js",
    [
        ("color:#7C3AED'", "color:#2F80ED'"),
        ("color:#7C3AED\"", "color:#2F80ED\""),
        ("border:1px solid rgba(124,58,237,0.18);", "border:1px solid #DCE4EE;"),
        ("this.style.borderColor='#7C3AED'", "this.style.borderColor='#2F80ED'"),
        ("rgba(124,58,237,0.15)", "rgba(47,128,237,0.15)"),
        ("this.style.borderColor='rgba(124,58,237,0.18)'", "this.style.borderColor='#DCE4EE'"),
        ("color:#17112B;", "color:#172B4D;"),
        ('["#DC2626", "#EC4899", "#D97706", "#F59E0B", "#7C3AED", "#8B5CF6", "#0284C7"]',
         '["#DC2626", "#2F80ED", "#D97706", "#F59E0B", "#123B66", "#16A6A1", "#0284C7"]'),
    ]
)
print("Updated remaining js lines!")
