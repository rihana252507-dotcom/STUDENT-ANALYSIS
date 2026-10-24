import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

backlog_html_block = """
        <!-- Backlog Details Breakdown Section -->
        <div id="modalBacklogsBreakdownSection" style="display:none; margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <h4 style="font-size:0.9rem; font-weight:700; color:#DC2626; margin:0; display:flex; align-items:center; gap:6px;">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              <span>Active Backlog Subjects</span>
            </h4>
            <span id="modalBacklogCountBadge" class="badge badge-high" style="font-size:0.72rem; padding:2px 8px;"></span>
          </div>
          <div id="modalBacklogSubjectsContainer" style="background:#FFFFFF; border:1px solid #DCE4EE; border-radius:8px; padding:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
          </div>
        </div>
"""

# Patch faculty_dashboard.html
fac_path = os.path.join(base_dir, "templates", "faculty_dashboard.html")
with open(fac_path, "r", encoding="utf-8") as f:
    fac_content = f.read()

norm_fac = fac_content.replace("\r\n", "\n")
fac_target = """          <div style="background:rgba(30,15,60,0.6); padding:10px; border-radius:8px; border:1px solid var(--border-glass); text-align:center;">
            <span style="font-size:0.68rem; color:#C4B5FD; text-transform:uppercase;">Technical</span>
            <div style="font-size:1.1rem; font-weight:800; color:#FFFFFF;" id="modalTech">75/100</div>
          </div>
        </div>"""

assert fac_target in norm_fac, "faculty modal target not found"
norm_fac = norm_fac.replace(fac_target, fac_target + "\n" + backlog_html_block.strip() + "\n", 1)

with open(fac_path, "w", encoding="utf-8") as f:
    f.write(norm_fac.replace("\n", "\r\n"))

print("Patched faculty_dashboard.html successfully!")

# Patch admin_dashboard.html
adm_path = os.path.join(base_dir, "templates", "admin_dashboard.html")
with open(adm_path, "r", encoding="utf-8") as f:
    adm_content = f.read()

norm_adm = adm_content.replace("\r\n", "\n")
assert fac_target in norm_adm, "admin modal target not found"
norm_adm = norm_adm.replace(fac_target, fac_target + "\n" + backlog_html_block.strip() + "\n", 1)

with open(adm_path, "w", encoding="utf-8") as f:
    f.write(norm_adm.replace("\n", "\r\n"))

print("Patched admin_dashboard.html successfully!")
