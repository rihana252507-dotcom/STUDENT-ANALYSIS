import re

HTML_PATH = r"c:\Users\samee\hackzelerate\STUDENT-ANALYSIS\templates\admin_dashboard.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Locate section-risk-monitoring
start_tag = '<section id="section-risk-monitoring"'
start_idx = html.find(start_tag)
assert start_idx != -1, "section-risk-monitoring start not found"

end_tag = '</section>'
end_idx = html.find(end_tag, start_idx)
assert end_idx != -1, "section-risk-monitoring end not found"

new_section_html = """<section id="section-risk-monitoring" class="dashboard-section">
        <!-- ── INITIAL VIEW: Clean list of At-Risk Students (Names & IDs only) ── -->
        <div id="adminRiskListView">
          <div class="hero-glass-banner">
            <div>
              <span class="hero-role-pill" style="background:linear-gradient(135deg, #F43F5E, #DC2626);">Early Risk Radar</span>
              <h2 class="hero-main-title">Risk Monitoring &amp; Student Watchlist</h2>
              <p class="hero-sub-desc">Proactive early detection of academic velocity, statutory attendance shortage, and backlog risks.</p>
            </div>
          </div>

          <div class="glass-card-container">
            <div class="glass-card-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
              <div>
                <h3 class="glass-card-title">At-Risk Students Requiring Mandatory Action</h3>
                <span class="glass-card-subtitle" style="display:block; margin-top:2px;">Click any student to view their detailed risk profile, circular attendance gauge, and backlog breakdown.</span>
              </div>
              <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                <input type="text" id="adminRiskSearchInput" class="cyber-input" style="max-width:280px; padding:6px 12px; font-size:0.8125rem; border-radius:6px;" placeholder="Search student name or ID..." oninput="filterAdminRiskList()">
                <span class="badge badge-high" id="adminRiskCountBadge">Loading...</span>
              </div>
            </div>
            <div class="glass-table-responsive">
              <table class="cyber-table">
                <thead>
                  <tr>
                    <th style="width:50%;">Student Name</th>
                    <th style="width:30%;">Student ID</th>
                    <th style="width:20%; text-align:right;">Action</th>
                  </tr>
                </thead>
                <tbody id="riskWatchlistBody">
                  <!-- Populated dynamically via JS: Student Names and IDs ONLY -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- ── DETAIL VIEW: Full Detailed Risk Profile (Hidden until a student is clicked) ── -->
        <div id="adminRiskDetailView" style="display:none;">
          <!-- Top Navigation / Back Button -->
          <div style="margin-bottom:18px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <button class="btn-action-secondary" onclick="closeAdminRiskDetail()" style="display:inline-flex; align-items:center; gap:8px; font-weight:600; cursor:pointer; padding:8px 16px; border-radius:8px; font-size:0.875rem;">
              &larr; Back to At-Risk Students List
            </button>
            <span style="font-size:0.8125rem; color:#6B7280;">Risk Profile Inspection Mode</span>
          </div>

          <!-- Student Header Card with Gender Avatar -->
          <div class="glass-card-container" style="margin-bottom:20px; padding:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
              <div style="display:flex; align-items:center; gap:16px;">
                <div id="riskDetailAvatarContainer">
                  <!-- Populated via JS with Gender Avatar -->
                </div>
                <div>
                  <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <h2 id="riskDetailName" style="font-size:1.35rem; font-weight:800; color:#111827; margin:0;">Student Name</h2>
                    <span id="riskDetailRiskBadge" class="badge badge-high">High Risk</span>
                    <span id="riskDetailScoreBadge" class="badge badge-accent">Success Score: 52/100</span>
                  </div>
                  <div style="font-size:0.8125rem; color:#4B5563; margin-top:4px;">
                    <span id="riskDetailID" style="font-weight:700; color:#5B21B6;">CIQ-2026-001</span> &bull; 
                    <span id="riskDetailDept">Computer Science</span> &bull; 
                    <span id="riskDetailSemYear">Semester 4 (Year 2)</span> &bull; 
                    Section <span id="riskDetailSection">A</span> &bull; 
                    Mentor: <strong id="riskDetailMentor" style="color:#111827;">Faculty Mentor</strong>
                  </div>
                </div>
              </div>
              <div style="display:flex; gap:8px; align-items:center;">
                <button class="btn-action-primary" style="font-size:0.8125rem; padding:8px 14px;" onclick="openInterventionForRiskStudent()">
                  + Assign Faculty Intervention
                </button>
              </div>
            </div>
          </div>

          <!-- Two-Column Grid: Attendance Gauge & Backlog Analysis -->
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(360px, 1fr)); gap:20px; margin-bottom:20px;">
            <!-- Circular Attendance Indicator Card -->
            <div class="glass-card-container" style="padding:20px;">
              <div class="glass-card-header" style="margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(229,231,235,0.8);">
                <h3 class="glass-card-title" style="font-size:1.05rem;">Attendance Indicator &amp; Analysis</h3>
                <span id="riskDetailAttStatusBadge" class="badge badge-high">Below Threshold</span>
              </div>
              <div style="display:flex; align-items:center; gap:24px; margin-bottom:16px; flex-wrap:wrap;">
                <!-- SVG Circular Progress Indicator -->
                <div style="position:relative; width:120px; height:120px; flex-shrink:0;">
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(203, 213, 225, 0.4)" stroke-width="10" />
                    <circle id="riskDetailAttCircle" cx="60" cy="60" r="48" fill="none" stroke="#DC2626" stroke-width="10"
                            stroke-dasharray="301.59" stroke-dashoffset="90" stroke-linecap="round"
                            transform="rotate(-90 60 60)" style="transition: stroke-dashoffset 0.8s ease;" />
                  </svg>
                  <div style="position:absolute; top:0; left:0; width:120px; height:120px; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                    <span id="riskDetailAttPercent" style="font-size:1.5rem; font-weight:800; color:#111827;">68%</span>
                    <span style="font-size:0.65rem; color:#6B7280; text-transform:uppercase; font-weight:700;">Overall</span>
                  </div>
                </div>
                <!-- Explanatory Text -->
                <div style="flex:1; min-width:180px;">
                  <div style="font-size:0.95rem; font-weight:700; color:#111827;" id="riskDetailAttLabel">Attendance: 68%</div>
                  <p id="riskDetailAttExplanation" style="font-size:0.8125rem; color:#4B5563; line-height:1.5; margin:6px 0 0;">
                    Statutory attendance threshold is 75.0%. Student requires urgent advisory counseling to avoid exam debarment.
                  </p>
                </div>
              </div>

              <!-- Subject-wise Attendance Breakdown -->
              <div style="margin-top:14px;">
                <h4 style="font-size:0.85rem; font-weight:700; color:#374151; margin-bottom:8px;">Subject-Wise Attendance Breakdown</h4>
                <div class="glass-table-responsive" style="max-height:180px; overflow-y:auto;">
                  <table class="cyber-table" style="font-size:0.75rem;">
                    <thead>
                      <tr>
                        <th>Subject</th>
                        <th>Sem</th>
                        <th>Attended / Total</th>
                        <th style="text-align:right;">Attendance %</th>
                      </tr>
                    </thead>
                    <tbody id="riskDetailSubjectAttBody">
                      <!-- Populated via JS -->
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- Backlog Analysis Card -->
            <div class="glass-card-container" style="padding:20px;">
              <div class="glass-card-header" style="margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(229,231,235,0.8);">
                <h3 class="glass-card-title" style="font-size:1.05rem;">Backlog Analysis</h3>
                <span id="riskDetailBacklogBadge" class="badge badge-high">2 Active Backlogs</span>
              </div>
              <div id="riskDetailBacklogSummary" style="margin-bottom:14px;">
                <!-- Summary text populated via JS -->
              </div>
              <div class="glass-table-responsive" style="max-height:220px; overflow-y:auto;">
                <table class="cyber-table" style="font-size:0.75rem;">
                  <thead>
                    <tr>
                      <th>Subject Code &amp; Name</th>
                      <th>Sem</th>
                      <th>Grade</th>
                      <th>Status</th>
                      <th style="text-align:right;">Marks (Int / Ext)</th>
                    </tr>
                  </thead>
                  <tbody id="riskDetailBacklogBody">
                    <!-- Populated via JS -->
                  </tbody>
                </table>
              </div>
              <p style="font-size:0.75rem; color:#6B7280; line-height:1.4; margin-top:10px;">
                * Backlogs impede academic velocity and graduation credit accumulation. Remedial tutoring and supplementary examination scheduling are required.
              </p>
            </div>
          </div>

          <!-- Section: Why This Student Is Flagged (Crucial explainable risk attribution) -->
          <div class="glass-card-container" style="padding:20px; margin-bottom:20px;">
            <div class="glass-card-header" style="margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(229,231,235,0.8);">
              <div>
                <h3 class="glass-card-title" style="font-size:1.1rem; color:#DC2626;">Why This Student Is Flagged</h3>
                <span class="glass-card-subtitle" style="display:block; margin-top:2px;">
                  Explainable attribution derived strictly from student database records and institutional risk thresholds.
                </span>
              </div>
              <span class="badge badge-high" id="riskDetailFactorsCount">Risk Drivers</span>
            </div>
            <div class="glass-table-responsive">
              <table class="cyber-table" style="font-size:0.8125rem;">
                <thead>
                  <tr>
                    <th style="width:20%;">Risk Factor</th>
                    <th style="width:25%;">Actual Evidence</th>
                    <th style="width:30%;">Reason for Concern</th>
                    <th style="width:25%;">Suggested Action</th>
                  </tr>
                </thead>
                <tbody id="riskDetailWhyFlaggedBody">
                  <!-- Populated via JS -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Section: CGPA, Marks, and Academic History -->
          <div class="glass-card-container" style="padding:20px; margin-bottom:20px;">
            <div class="glass-card-header" style="margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(229,231,235,0.8); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
              <div>
                <h3 class="glass-card-title" style="font-size:1.1rem;">Academic History &amp; Performance</h3>
                <span class="glass-card-subtitle" style="display:block; margin-top:2px;">
                  Cumulative Grade Point Average (CGPA), semester-wise SGPA progression, and subject evaluations.
                </span>
              </div>
              <div style="display:flex; align-items:center; gap:12px;">
                <span class="badge badge-accent" id="riskDetailCGPABadge" style="font-size:0.875rem; padding:6px 12px;">CGPA: 5.85 / 10.0</span>
              </div>
            </div>

            <!-- SGPA Progression Row -->
            <div style="margin-bottom:16px;">
              <h4 style="font-size:0.8125rem; font-weight:700; color:#374151; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.04em;">Semester-Wise SGPA Progression</h4>
              <div id="riskDetailSgpaContainer" style="display:flex; gap:10px; flex-wrap:wrap;">
                <!-- SGPA pills populated via JS -->
              </div>
            </div>

            <!-- Subject-wise Academic Marks Table -->
            <h4 style="font-size:0.8125rem; font-weight:700; color:#374151; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.04em;">Comprehensive Subject-Wise Evaluations</h4>
            <div class="glass-table-responsive" style="max-height:280px; overflow-y:auto;">
              <table class="cyber-table" style="font-size:0.75rem;">
                <thead>
                  <tr>
                    <th>Sem</th>
                    <th>Course Code &amp; Name</th>
                    <th>Credits</th>
                    <th>Mid 1</th>
                    <th>Mid 2</th>
                    <th>Internal (40)</th>
                    <th>External (60)</th>
                    <th>Total (100)</th>
                    <th>Grade</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody id="riskDetailAcademicMarksBody">
                  <!-- Populated via JS -->
                </tbody>
              </table>
            </div>
          </div>

          <!-- Section: Composite Success Score, 5 Pillars & Recommended Actions -->
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(340px, 1fr)); gap:20px;">
            <!-- Pillar Breakdown Card -->
            <div class="glass-card-container" style="padding:20px;">
              <div class="glass-card-header" style="margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(229,231,235,0.8);">
                <h3 class="glass-card-title" style="font-size:1.05rem;">Multi-Pillar Success Diagnostics</h3>
                <span class="badge badge-accent" id="riskDetailCompositeScore">Composite: 58.4/100</span>
              </div>
              <div id="riskDetailPillarsBody" style="display:flex; flex-direction:column; gap:10px;">
                <!-- 5 Pillar bars populated via JS -->
              </div>
            </div>

            <!-- Recommended Actions Card -->
            <div class="glass-card-container" style="padding:20px;">
              <div class="glass-card-header" style="margin-bottom:12px; padding-bottom:8px; border-bottom:1px solid rgba(229,231,235,0.8);">
                <h3 class="glass-card-title" style="font-size:1.05rem;">Recommended Actions</h3>
                <span class="badge badge-low">Action Roadmap</span>
              </div>
              <div id="riskDetailRecommendationsBody" style="display:flex; flex-direction:column; gap:10px;">
                <!-- Recommendations populated via JS -->
              </div>
            </div>
          </div>
        </div>
      </section>"""

# Replace in html
html = html[:start_idx] + new_section_html + html[end_idx + len(end_tag):]

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("admin_dashboard.html updated successfully with clean list + detail risk view!")
