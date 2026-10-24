"""Fix remaining mismatches from first run."""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS"

def replace_in_file(path, old, new, description):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"  [WARN] Not found: {description}")
        return False
    count = content.count(old)
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {description} ({count} occurrence(s))")
    return True

admin_html = BASE + r"\templates\admin_dashboard.html"

# Placement KPI 2 and 3 — HTML uses bare & not &amp; inside these spans
replace_in_file(admin_html,
    '<span style="font-size:0.75rem; color:#D4E9FF;">Quantitative, Logical & Verbal</span>',
    '<span style="font-size:0.75rem; color:#5B6B82;">Quantitative, Logical & Verbal</span>',
    "Placement KPI 2 sub-label color")

replace_in_file(admin_html,
    '<span style="font-size:0.75rem; color:#D4E9FF;">Algorithms, Coding & Architecture</span>',
    '<span style="font-size:0.75rem; color:#5B6B82;">Algorithms, Coding & Architecture</span>',
    "Placement KPI 3 sub-label color")

# Settings section — read exact text, do precise sub-replacements
with open(admin_html, "r", encoding="utf-8") as f:
    content = f.read()

# Fix all 5 settings cards: replace dark bg + label/desc colors inside section-settings
# Pattern is consistent: background:rgba(30,15,60,0.6) -> #F4F7FB, border-glass -> DCE4EE,
# color:#C4B5FD -> #5B6B82,  color:#D4E9FF (in settings block) -> #5B6B82

# Locate the settings section and work only within it
settings_start = content.find('<section id="section-settings"')
settings_end = content.find('</section>', settings_start) + len('</section>')
if settings_start < 0:
    print("  [WARN] section-settings not found!")
else:
    settings_block = content[settings_start:settings_end]
    # 1. Replace dark card backgrounds
    new_block = settings_block.replace(
        'background:rgba(30,15,60,0.6); padding:16px; border-radius:10px; border:1px solid var(--border-glass);',
        'background:#F4F7FB; padding:16px; border-radius:10px; border:1px solid #DCE4EE;'
    )
    # 2. Replace label colors inside these cards
    new_block = new_block.replace(
        'font-size:0.75rem; color:#C4B5FD; font-weight:700;',
        'font-size:0.75rem; color:#5B6B82; font-weight:700;'
    )
    # 3. Replace desc colors (0.72rem)
    new_block = new_block.replace(
        'font-size:0.72rem; color:#D4E9FF;',
        'font-size:0.72rem; color:#5B6B82;'
    )
    if new_block != settings_block:
        content = content[:settings_start] + new_block + content[settings_end:]
        with open(admin_html, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] Settings section — dark cards fixed")
    else:
        print("  [WARN] Settings section — no changes made (already fixed or different markup)")

# Faculty save button labels
faculty_html = BASE + r"\templates\faculty_dashboard.html"
replace_in_file(faculty_html,
    '>Save to SQLite</button>',
    '>Save Intervention</button>',
    "faculty: Save to SQLite -> Save Intervention")
replace_in_file(faculty_html,
    '>Save Progress to SQLite</button>',
    '>Save Progress</button>',
    "faculty: Save Progress to SQLite -> Save Progress")

print("\nAll remaining fixes applied.")
