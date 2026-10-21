import re

# Paths
ADMIN_HTML = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html"
FAC_HTML   = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\faculty_dashboard.html"
STU_HTML   = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\student_dashboard.html"
CSS_PATH   = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\static\css\style.css"

# ── 1. Update templates/admin_dashboard.html ──
with open(ADMIN_HTML, "r", encoding="utf-8") as f:
    admin = f.read()

admin_old_sim = """      <div class="glass-modal-header">
        <div>
          <h3 style="color:#FFFFFF; font-size:1.25rem; font-weight:800;">CampusIQ What-If Academic Simulator</h3>
          <p style="font-size:0.78rem; color:#DDD6FE;">Simulate the exact numerical impact of faculty intervention on student risk categories.</p>
        </div>
        <button id="btnCloseSimulator" class="btn-close-modal-icon">&times;</button>
      </div>

      <div class="glass-modal-body">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <label for="simStudentSelect" style="font-weight:700; font-size:0.85rem; color:#C4B5FD;">Select Student:</label>
          <select id="simStudentSelect" class="cyber-select" style="flex:1;"></select>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
          <div style="display:flex; flex-direction:column; gap:12px;">
            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                <label>Attendance Boost:</label>
                <strong id="valSimAttendance" style="color:#EC4899;">+10%</strong>
              </div>
              <input type="range" id="rangeSimAttendance" min="0" max="30" value="10" step="1" style="accent-color:#EC4899;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                <label>Backlogs Cleared:</label>
                <strong id="valSimBacklogs" style="color:#EC4899;">1 Backlog</strong>
              </div>
              <input type="range" id="rangeSimBacklogs" min="0" max="3" value="1" step="1" style="accent-color:#EC4899;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                <label>Weekly LMS Hours:</label>
                <strong id="valSimLms" style="color:#EC4899;">+5 hrs/wk</strong>
              </div>
              <input type="range" id="rangeSimLms" min="0" max="15" value="5" step="1" style="accent-color:#EC4899;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.78rem;">
                <label>Assignment Rate Boost:</label>
                <strong id="valSimAssignment" style="color:#EC4899;">+15%</strong>
              </div>
              <input type="range" id="rangeSimAssignment" min="0" max="30" value="15" step="1" style="accent-color:#EC4899;">
            </div>

            <button id="btnRunSimulation" class="btn-action-primary" style="justify-content:center; margin-top:8px;">Recalculate Score</button>
          </div>

          <div style="display:flex; flex-direction:column; justify-content:space-between;">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
              <div style="flex:1; background:rgba(35,18,70,0.6); border:1px solid var(--border-glass); border-radius:12px; padding:14px; text-align:center;">
                <span style="font-size:0.7rem; color:#A78BFA; font-weight:700;">CURRENT</span>
                <div style="font-size:1.8rem; font-weight:800; color:#FFFFFF;" id="simCurrentScore">--</div>
                <div id="simCurrentBadge" class="badge badge-high">High Risk</div>
              </div>

              <span style="color:#EC4899; font-size:1.2rem; font-weight:800;">&rarr;</span>

              <div style="flex:1; background:rgba(35,18,70,0.6); border:1px solid var(--border-glass); border-radius:12px; padding:14px; text-align:center;">
                <span style="font-size:0.7rem; color:#A78BFA; font-weight:700;">SIMULATED</span>
                <div style="font-size:1.8rem; font-weight:800; color:#10B981;" id="simProjectedScore">--</div>
                <div id="simProjectedBadge" class="badge badge-low">Low Risk</div>
              </div>
            </div>

            <div style="background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:14px; margin-top:12px;">
              <strong style="color:#6EE7B7; font-size:0.875rem;" id="simDeltaHighlight">Success Score Delta: +14.5 pts</strong>
              <p style="color:#D1FAE5; font-size:0.78rem; margin-top:4px;" id="simRecommendationText">
                Simulated remediation effectively clears statutory thresholds!
              </p>
            </div>
          </div>
        </div>"""

admin_new_sim = """      <div class="glass-modal-header" style="background:#FAF9FE; border-bottom:1px solid #E5E7EB; padding:16px 20px;">
        <div>
          <h3 style="color:#111827; font-size:1.25rem; font-weight:800; margin:0;">CampusIQ What-If Academic Simulator</h3>
          <p style="font-size:0.8125rem; color:#4B5563; margin-top:3px; margin-bottom:0;">Simulate the exact numerical impact of faculty intervention on student risk categories.</p>
        </div>
        <button id="btnCloseSimulator" class="btn-close-modal-icon" style="color:#374151;">&times;</button>
      </div>

      <div class="glass-modal-body" style="padding:20px; background:#FFFFFF;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:14px;">
          <label for="simStudentSelect" style="font-weight:700; font-size:0.85rem; color:#1F2937;">Select Student:</label>
          <select id="simStudentSelect" class="cyber-select" style="flex:1; background:#FFFFFF; color:#111827; border:1px solid #D1D5DB; font-weight:600;"></select>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
          <div style="display:flex; flex-direction:column; gap:14px;">
            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                <label style="color:#1F2937; font-weight:700; font-size:0.8125rem;">Attendance Boost:</label>
                <strong id="valSimAttendance" style="color:#DB2777; font-weight:800;">+10%</strong>
              </div>
              <input type="range" id="rangeSimAttendance" min="0" max="30" value="10" step="1" style="accent-color:#DB2777; width:100%;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                <label style="color:#1F2937; font-weight:700; font-size:0.8125rem;">Backlogs Cleared:</label>
                <strong id="valSimBacklogs" style="color:#7C3AED; font-weight:800;">1 Backlog</strong>
              </div>
              <input type="range" id="rangeSimBacklogs" min="0" max="3" value="1" step="1" style="accent-color:#7C3AED; width:100%;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                <label style="color:#1F2937; font-weight:700; font-size:0.8125rem;">Weekly LMS Hours:</label>
                <strong id="valSimLms" style="color:#0284C7; font-weight:800;">+5 hrs/wk</strong>
              </div>
              <input type="range" id="rangeSimLms" min="0" max="15" value="5" step="1" style="accent-color:#0284C7; width:100%;">
            </div>

            <div class="input-group-custom" style="margin-bottom:0;">
              <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                <label style="color:#1F2937; font-weight:700; font-size:0.8125rem;">Assignment Rate Boost:</label>
                <strong id="valSimAssignment" style="color:#059669; font-weight:800;">+15%</strong>
              </div>
              <input type="range" id="rangeSimAssignment" min="0" max="30" value="15" step="1" style="accent-color:#059669; width:100%;">
            </div>

            <button id="btnRunSimulation" class="btn-action-primary" style="justify-content:center; margin-top:8px;">Recalculate Score</button>
          </div>

          <div style="display:flex; flex-direction:column; justify-content:space-between; gap:14px;">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
              <div style="flex:1; background:#FAF9FE; border:1px solid #E5E7EB; border-radius:12px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; color:#6B21A8; font-weight:800; letter-spacing:0.04em;">CURRENT</span>
                <div style="font-size:1.8rem; font-weight:800; color:#111827;" id="simCurrentScore">--</div>
                <div id="simCurrentBadge" class="badge badge-high">High Risk</div>
              </div>

              <span style="color:#7C3AED; font-size:1.4rem; font-weight:800;">&rarr;</span>

              <div style="flex:1; background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px; padding:14px; text-align:center;">
                <span style="font-size:0.75rem; color:#065F46; font-weight:800; letter-spacing:0.04em;">SIMULATED</span>
                <div style="font-size:1.8rem; font-weight:800; color:#059669;" id="simProjectedScore">--</div>
                <div id="simProjectedBadge" class="badge badge-low">Low Risk</div>
              </div>
            </div>

            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:14px; margin-top:6px;">
              <strong style="color:#065F46; font-size:0.875rem; display:block;" id="simDeltaHighlight">Success Score Delta: +14.5 pts</strong>
              <p style="color:#047857; font-size:0.8125rem; margin-top:4px; margin-bottom:0; line-height:1.5; font-weight:500;" id="simRecommendationText">
                Simulated remediation effectively clears statutory thresholds!
              </p>
            </div>
          </div>
        </div>"""

# Match normalized line endings
def safe_replace(content, old, new):
    norm_content = content.replace("\r\n", "\n")
    norm_old = old.replace("\r\n", "\n")
    norm_new = new.replace("\r\n", "\n")
    if norm_old in norm_content:
        # Keep original line endings of the file
        if "\r\n" in content:
            return norm_content.replace(norm_old, norm_new).replace("\n", "\r\n")
        else:
            return norm_content.replace(norm_old, norm_new)
    raise ValueError("Target snippet not found in file")

admin_updated = safe_replace(admin, admin_old_sim, admin_new_sim)
with open(ADMIN_HTML, "w", encoding="utf-8") as f:
    f.write(admin_updated)
print("Updated templates/admin_dashboard.html")

# ── 2. Update templates/faculty_dashboard.html ──
with open(FAC_HTML, "r", encoding="utf-8") as f:
    fac = f.read()

fac_old_sim = admin_old_sim.replace("Select Student:", "Select Advisee:").replace("on student risk categories", "on advisee risk categories")
fac_new_sim = admin_new_sim.replace("Select Student:", "Select Advisee:").replace("on student risk categories", "on advisee risk categories")

fac_updated = safe_replace(fac, fac_old_sim, fac_new_sim)
with open(FAC_HTML, "w", encoding="utf-8") as f:
    f.write(fac_updated)
print("Updated templates/faculty_dashboard.html")

# ── 3. Update templates/student_dashboard.html ──
with open(STU_HTML, "r", encoding="utf-8") as f:
    stu = f.read()

stu_old_sim = """            <div style="font-size:0.85rem; color:#E9D5FF; line-height:1.6; margin-bottom:16px;">
              CampusIQ computes your Success Score using a multi-factor mathematical model designed specifically for early risk intervention:
            </div>

            <div style="background:rgba(20, 10, 42, 0.7); border:1px solid rgba(196, 181, 253, 0.2); border-radius:12px; padding:16px; margin-bottom:16px;">
              <div style="font-family:monospace; font-size:0.85rem; color:#F472B6; margin-bottom:8px;">
                Success Score = (0.30 &times; Academic) + (0.20 &times; Attendance) + (0.15 &times; LMS) + (0.20 &times; Placement) + (0.15 &times; Wellbeing)
              </div>
              <div style="font-size:0.75rem; color:#C4B5FD;">
                Each pillar maps raw data (CGPA, biometric logs, LMS hours, aptitude scores) to a normalized 0-100 scale with severe penalties for backlogs and sub-75% attendance.
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; padding:14px 16px; background:rgba(139, 92, 246, 0.15); border-radius:10px;">
              <div>
                <span style="font-size:0.75rem; color:#C4B5FD; display:block;">Your Current Composite Score</span>
                <span style="font-size:1.8rem; font-weight:800; color:#FFFFFF;">{{ student.success_score }} / 100</span>
              </div>
              <span class="badge badge-{{ student.risk_badge or (student.risk_level.lower() if student.risk_level else 'neutral') }}" style="font-size:0.9rem; padding:6px 14px;">
                {{ student.risk_level or 'Not available' }} Risk
              </span>
            </div>
          </div>

          <!-- Interactive What-If Simulator Panel -->
          <div class="glass-card">
            <div class="glass-card-header">
              <div>
                <h3 class="glass-card-title">Interactive What-If Simulator</h3>
                <p class="glass-card-subtitle">Simulate how improving your habits elevates your projected score</p>
              </div>
              <span class="badge badge-accent">Live Forecast</span>
            </div>

            <div class="simulator-slider-group" style="display:flex; flex-direction:column; gap:16px; margin-top:8px;">
              
              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <label for="personalRangeAttendance"><strong>Boost Attendance</strong></label>
                  <span id="personalValAttendance" style="color:#EC4899; font-weight:700;">+0%</span>
                </div>
                <input type="range" id="personalRangeAttendance" min="0" max="25" step="1" value="0" style="width:100%; accent-color:#EC4899;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <label for="personalRangeBacklogs"><strong>Clear Active Backlogs</strong></label>
                  <span id="personalValBacklogs" style="color:#8B5CF6; font-weight:700;">0 Cleared</span>
                </div>
                <input type="range" id="personalRangeBacklogs" min="0" max="{{ student.backlogs if student.backlogs > 0 else 2 }}" step="1" value="0" style="width:100%; accent-color:#8B5CF6;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <label for="personalRangeLms"><strong>Increase Weekly Study Hours</strong></label>
                  <span id="personalValLms" style="color:#06B6D4; font-weight:700;">+0 hrs/wk</span>
                </div>
                <input type="range" id="personalRangeLms" min="0" max="15" step="1" value="0" style="width:100%; accent-color:#06B6D4;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <label for="personalRangeAssignment"><strong>Boost Assignment Completion</strong></label>
                  <span id="personalValAssignment" style="color:#10B981; font-weight:700;">+0%</span>
                </div>
                <input type="range" id="personalRangeAssignment" min="0" max="20" step="1" value="0" style="width:100%; accent-color:#10B981;">
              </div>

              <div style="display:flex; gap:12px; margin-top:6px;">
                <button id="btnRunPersonalSim" class="btn-action-primary" style="flex:1;">
                  Calculate Projected Impact
                </button>
              </div>

              <!-- Simulator Outcome Display -->
              <div id="personalSimResults" style="padding:14px; background:rgba(236, 72, 153, 0.12); border:1px solid rgba(236, 72, 153, 0.3); border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span style="font-size:0.75rem; color:#DDD6FE; display:block;">Projected Success Score</span>
                  <div style="display:flex; align-items:baseline; gap:8px;">
                    <span id="personalProjectedScore" style="font-size:1.6rem; font-weight:800; color:#FFFFFF;">{{ student.success_score }}</span>
                    <span id="personalDeltaText" style="font-size:0.8rem; color:#34D399; font-weight:700;">(+0.0 pts)</span>
                  </div>
                </div>
                <span id="personalProjectedBadge" class="badge badge-{{ student.risk_badge or (student.risk_level.lower() if student.risk_level else 'neutral') }}">
                  {{ student.risk_level or 'Not available' }} Risk
                </span>
              </div>"""

stu_new_sim = """            <div style="font-size:0.875rem; color:#374151; line-height:1.6; margin-bottom:16px; font-weight:500;">
              CampusIQ computes your Success Score using a multi-factor mathematical model designed specifically for early risk intervention:
            </div>

            <div style="background:#1E1538; border:1px solid #7C3AED; border-radius:12px; padding:16px; margin-bottom:16px;">
              <div style="font-family:monospace; font-size:0.875rem; color:#F472B6; font-weight:700; margin-bottom:8px;">
                Success Score = (0.30 &times; Academic) + (0.20 &times; Attendance) + (0.15 &times; LMS) + (0.20 &times; Placement) + (0.15 &times; Wellbeing)
              </div>
              <div style="font-size:0.8125rem; color:#E0E7FF; line-height:1.5;">
                Each pillar maps raw data (CGPA, biometric logs, LMS hours, aptitude scores) to a normalized 0-100 scale with severe penalties for backlogs and sub-75% attendance.
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; padding:14px 16px; background:#F5F3FF; border:1px solid #DDD6FE; border-radius:10px;">
              <div>
                <span style="font-size:0.75rem; color:#5B21B6; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; display:block;">Your Current Composite Score</span>
                <span style="font-size:1.8rem; font-weight:800; color:#111827;">{{ student.success_score }} / 100</span>
              </div>
              <span class="badge badge-{{ student.risk_badge or (student.risk_level.lower() if student.risk_level else 'neutral') }}" style="font-size:0.9rem; padding:6px 14px;">
                {{ student.risk_level or 'Not available' }} Risk
              </span>
            </div>
          </div>

          <!-- Interactive What-If Simulator Panel -->
          <div class="glass-card">
            <div class="glass-card-header">
              <div>
                <h3 class="glass-card-title">Interactive What-If Simulator</h3>
                <p class="glass-card-subtitle">Simulate how improving your habits elevates your projected score</p>
              </div>
              <span class="badge badge-accent">Live Forecast</span>
            </div>

            <div class="simulator-slider-group" style="display:flex; flex-direction:column; gap:16px; margin-top:8px;">
              
              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                  <label for="personalRangeAttendance" style="color:#1F2937; font-weight:700;"><strong>Boost Attendance</strong></label>
                  <span id="personalValAttendance" style="color:#DB2777; font-weight:800;">+0%</span>
                </div>
                <input type="range" id="personalRangeAttendance" min="0" max="25" step="1" value="0" style="width:100%; accent-color:#DB2777;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                  <label for="personalRangeBacklogs" style="color:#1F2937; font-weight:700;"><strong>Clear Active Backlogs</strong></label>
                  <span id="personalValBacklogs" style="color:#7C3AED; font-weight:800;">0 Cleared</span>
                </div>
                <input type="range" id="personalRangeBacklogs" min="0" max="{{ student.backlogs if student.backlogs > 0 else 2 }}" step="1" value="0" style="width:100%; accent-color:#7C3AED;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                  <label for="personalRangeLms" style="color:#1F2937; font-weight:700;"><strong>Increase Weekly Study Hours</strong></label>
                  <span id="personalValLms" style="color:#0284C7; font-weight:800;">+0 hrs/wk</span>
                </div>
                <input type="range" id="personalRangeLms" min="0" max="15" step="1" value="0" style="width:100%; accent-color:#0284C7;">
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8125rem; margin-bottom:4px;">
                  <label for="personalRangeAssignment" style="color:#1F2937; font-weight:700;"><strong>Boost Assignment Completion</strong></label>
                  <span id="personalValAssignment" style="color:#059669; font-weight:800;">+0%</span>
                </div>
                <input type="range" id="personalRangeAssignment" min="0" max="20" step="1" value="0" style="width:100%; accent-color:#059669;">
              </div>

              <div style="display:flex; gap:12px; margin-top:6px;">
                <button id="btnRunPersonalSim" class="btn-action-primary" style="flex:1;">
                  Calculate Projected Impact
                </button>
              </div>

              <!-- Simulator Outcome Display -->
              <div id="personalSimResults" style="padding:14px 16px; background:#FDF2F8; border:1px solid #FBCFE8; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span style="font-size:0.75rem; color:#831843; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; display:block;">Projected Success Score</span>
                  <div style="display:flex; align-items:baseline; gap:8px;">
                    <span id="personalProjectedScore" style="font-size:1.6rem; font-weight:800; color:#111827;">{{ student.success_score }}</span>
                    <span id="personalDeltaText" style="font-size:0.875rem; color:#059669; font-weight:800;">(+0.0 pts)</span>
                  </div>
                </div>
                <span id="personalProjectedBadge" class="badge badge-{{ student.risk_badge or (student.risk_level.lower() if student.risk_level else 'neutral') }}">
                  {{ student.risk_level or 'Not available' }} Risk
                </span>
              </div>"""

stu_updated = safe_replace(stu, stu_old_sim, stu_new_sim)
with open(STU_HTML, "w", encoding="utf-8") as f:
    f.write(stu_updated)
print("Updated templates/student_dashboard.html")

# ── 4. Append Scoped CSS to static/css/style.css ──
with open(CSS_PATH, "r", encoding="utf-8") as f:
    css = f.read()

SCOPED_SIM_CSS = """
/* ==============================================================================
   SCOPED STYLES: CAMPUSIQ WHAT-IF SIMULATOR VISIBILITY & READABILITY FIX
   Scope: #simulatorModal (Admin & Faculty) & #section-my-success-score (Student)
   ============================================================================== */

#simulatorModal .glass-modal-header h3 {
  color: #111827 !important;
  font-weight: 800;
}

#simulatorModal .glass-modal-header p {
  color: #4B5563 !important;
}

#simulatorModal label,
#simulatorModal .input-group-custom label {
  color: #1F2937 !important;
  font-weight: 700;
  text-transform: none;
  letter-spacing: normal;
}

#simulatorModal select.cyber-select {
  background-color: #FFFFFF !important;
  color: #111827 !important;
  border-color: #D1D5DB !important;
}

#simulatorModal select.cyber-select option {
  background-color: #FFFFFF !important;
  color: #111827 !important;
  padding: 6px 10px;
}

#simulatorModal #simDeltaHighlight {
  color: #065F46 !important;
}

#simulatorModal #simRecommendationText {
  color: #047857 !important;
  font-weight: 500;
}

#section-my-success-score label,
.simulator-slider-group label {
  color: #1F2937 !important;
  font-weight: 700;
}

#personalSimResults #personalProjectedScore {
  color: #111827 !important;
  font-weight: 800;
}

#personalSimResults #personalDeltaText {
  color: #059669 !important;
  font-weight: 800;
}
"""

if "SCOPED STYLES: CAMPUSIQ WHAT-IF SIMULATOR VISIBILITY" not in css:
    css = css + "\n" + SCOPED_SIM_CSS
    with open(CSS_PATH, "w", encoding="utf-8") as f:
        f.write(css)
    print("Appended scoped simulator styles to static/css/style.css")
else:
    print("Scoped styles already present in style.css")

print("\nAll files successfully updated!")
