import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl_path = os.path.join(base_dir, "templates", "student_dashboard.html")

with open(tpl_path, "r", encoding="utf-8") as f:
    content = f.read()

norm_content = content.replace("\r\n", "\n")

# 1. Notifications dropdown text readability
old_notif = """            <div class="notification-item unread">
              <div class="notification-title">{{ n.title }}</div>
              <p style="color:#D4E9FF; font-size:0.75rem;">{{ n.message }}</p>
              <div class="notification-time">{{ n.created_at or 'Today' }}</div>
            </div>
            {% endfor %}
          {% else %}
            <div class="notification-item">
              <div class="notification-title">Academic Telemetry Synchronized</div>
              <p style="color:#D4E9FF; font-size:0.75rem;">Continuous evaluation metrics and biometric logs are up to date.</p>"""

new_notif = """            <div class="notification-item unread">
              <div class="notification-title">{{ n.title }}</div>
              <p style="color:#5B6B82; font-size:0.75rem;">{{ n.message }}</p>
              <div class="notification-time">{{ n.created_at or 'Today' }}</div>
            </div>
            {% endfor %}
          {% else %}
            <div class="notification-item">
              <div class="notification-title">Academic Telemetry Synchronized</div>
              <p style="color:#5B6B82; font-size:0.75rem;">Continuous evaluation metrics and biometric logs are up to date.</p>"""

assert old_notif in norm_content, "old_notif target not found"
norm_content = norm_content.replace(old_notif, new_notif, 1)

# 2. Overall attendance big number & description readability
old_att_card = """            <div style="text-align:center; padding:24px 0;">
              <div style="font-size:3.5rem; font-weight:800; font-family:var(--font-heading);" class="text-gradient-purple">
                {{ student.attendance_pct ~ '%' if student.attendance_pct is not none else 'N/A' }}
              </div>
              <p style="font-size:0.85rem; color:#D4E9FF; max-width:400px; margin:8px auto;">"""

new_att_card = """            <div style="text-align:center; padding:24px 0;">
              <div style="font-size:3.5rem; font-weight:800; font-family:var(--font-heading); color:{% if student.attendance_pct is not none and student.attendance_pct < 75 %}#DC2626{% else %}#172B4D{% endif %};">
                {{ student.attendance_pct ~ '%' if student.attendance_pct is not none else 'N/A' }}
              </div>
              <p style="font-size:0.85rem; color:#5B6B82; max-width:400px; margin:8px auto; font-weight:500;">"""

assert old_att_card in norm_content, "old_att_card target not found"
norm_content = norm_content.replace(old_att_card, new_att_card, 1)

# 3. Dynamic Course-wise attendance breakdown
old_breakdown = """            <div style="display:flex; flex-direction:column; gap:14px; margin-top:10px;">
              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <span>Algorithms & Problem Solving (44/48 attended)</span>
                  <span style="color:#34D399; font-weight:700;">91.6%</span>
                </div>
                <div class="table-progress-bar" style="height:6px;">
                  <div class="table-progress-fill" style="width: 91.6%; background:#34D399;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <span>Database Systems (40/46 attended)</span>
                  <span style="color:#34D399; font-weight:700;">86.9%</span>
                </div>
                <div class="table-progress-bar" style="height:6px;">
                  <div class="table-progress-fill" style="width: 86.9%; background:#34D399;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <span>Operating Systems Lab (26/30 attended)</span>
                  <span style="color:#34D399; font-weight:700;">86.6%</span>
                </div>
                <div class="table-progress-bar" style="height:6px;">
                  <div class="table-progress-fill" style="width: 86.6%; background:#34D399;"></div>
                </div>
              </div>

              <div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px;">
                  <span>Machine Learning Systems (38/44 attended)</span>
                  <span style="color:#34D399; font-weight:700;">86.3%</span>
                </div>
                <div class="table-progress-bar" style="height:6px;">
                  <div class="table-progress-fill" style="width: 86.3%; background:#34D399;"></div>
                </div>
              </div>
            </div>"""

new_breakdown = """            <div style="display:flex; flex-direction:column; gap:14px; margin-top:10px;">
              {% set current_courses = [] %}
              {% if academic_records %}
                {% for rec in academic_records %}
                  {% if rec.semester == student.semester and rec.classes_conducted and rec.classes_conducted > 0 %}
                    {% set _ = current_courses.append(rec) %}
                  {% endif %}
                {% endfor %}
              {% endif %}

              {% if current_courses %}
                {% for rec in current_courses %}
                  <div>
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px; color:#172B4D;">
                      <span style="font-weight:600;">{{ rec.course_name }}{% if rec.course_code %} ({{ rec.course_code }}){% endif %} <span style="color:#5B6B82; font-weight:normal;">&bull; {{ rec.classes_attended }}/{{ rec.classes_conducted }} attended</span></span>
                      <span style="color:{% if rec.attendance_pct < 75 %}#DC2626{% else %}#16A34A{% endif %}; font-weight:700;">{{ rec.attendance_pct }}%</span>
                    </div>
                    <div class="table-progress-bar" style="height:6px;">
                      <div class="table-progress-fill" style="width: {{ rec.attendance_pct }}%; background:{% if rec.attendance_pct < 75 %}#DC2626{% else %}#16A34A{% endif %};"></div>
                    </div>
                  </div>
                {% endfor %}
              {% elif academic_records %}
                {% for rec in academic_records[:6] %}
                  {% if rec.classes_conducted and rec.classes_conducted > 0 %}
                    <div>
                      <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:4px; color:#172B4D;">
                        <span style="font-weight:600;">{{ rec.course_name }}{% if rec.course_code %} ({{ rec.course_code }}){% endif %} <span style="color:#5B6B82; font-weight:normal;">&bull; {{ rec.classes_attended }}/{{ rec.classes_conducted }} attended</span></span>
                        <span style="color:{% if rec.attendance_pct < 75 %}#DC2626{% else %}#16A34A{% endif %}; font-weight:700;">{{ rec.attendance_pct }}%</span>
                      </div>
                      <div class="table-progress-bar" style="height:6px;">
                        <div class="table-progress-fill" style="width: {{ rec.attendance_pct }}%; background:{% if rec.attendance_pct < 75 %}#DC2626{% else %}#16A34A{% endif %};"></div>
                      </div>
                    </div>
                  {% endif %}
                {% endfor %}
              {% else %}
                <p style="color:#5B6B82; font-size:0.85rem; padding:8px 0;">No course-level attendance records available for this semester.</p>
              {% endif %}
            </div>"""

assert old_breakdown in norm_content, "old_breakdown target not found"
norm_content = norm_content.replace(old_breakdown, new_breakdown, 1)

# 4. Assignments & LMS telemetry cards readability
old_assignments = """        <div class="grid-3-col" style="margin-bottom:24px;">
          <div class="glass-card">
            <span class="kpi-label">Assignment Submission Rate</span>
            <div class="kpi-value text-gradient-purple" style="margin:8px 0;">{{ student.assignment_completion_pct }}%</div>
            <p style="font-size:0.75rem; color:#D4E9FF;">Total assignments submitted before deadline</p>
          </div>

          <div class="glass-card">
            <span class="kpi-label">LMS Weekly Learning Hours</span>
            <div class="kpi-value text-gradient-pink" style="margin:8px 0;">{{ student.lms_weekly_hours }}<span class="kpi-sub"> hrs/wk</span></div>
            <p style="font-size:0.75rem; color:#D4E9FF;">Active study & coding lab time on LMS portal</p>
          </div>

          <div class="glass-card">
            <span class="kpi-label">Digital Engagement Index</span>
            <div class="kpi-value text-gradient-purple" style="margin:8px 0;">{{ student.lms_engagement_score }}<span class="kpi-sub">/100</span></div>
            <p style="font-size:0.75rem; color:#D4E9FF;">Forum participation and lab exercises completed</p>
          </div>
        </div>"""

new_assignments = """        <div class="grid-3-col" style="margin-bottom:24px;">
          <div class="glass-card">
            <span class="kpi-label">Assignment Submission Rate</span>
            <div class="kpi-value" style="margin:8px 0; color:#172B4D;">{{ student.assignment_completion_pct }}%</div>
            <p style="font-size:0.75rem; color:#5B6B82;">Total assignments submitted before deadline</p>
          </div>

          <div class="glass-card">
            <span class="kpi-label">LMS Weekly Learning Hours</span>
            <div class="kpi-value" style="margin:8px 0; color:#172B4D;">{{ student.lms_weekly_hours }}<span class="kpi-sub" style="color:#5B6B82;"> hrs/wk</span></div>
            <p style="font-size:0.75rem; color:#5B6B82;">Active study & coding lab time on LMS portal</p>
          </div>

          <div class="glass-card">
            <span class="kpi-label">Digital Engagement Index</span>
            <div class="kpi-value" style="margin:8px 0; color:#172B4D;">{{ student.lms_engagement_score }}<span class="kpi-sub" style="color:#5B6B82;">/100</span></div>
            <p style="font-size:0.75rem; color:#5B6B82;">Forum participation and lab exercises completed</p>
          </div>
        </div>"""

assert old_assignments in norm_content, "old_assignments target not found"
norm_content = norm_content.replace(old_assignments, new_assignments, 1)

with open(tpl_path, "w", encoding="utf-8") as f:
    f.write(norm_content.replace("\n", "\r\n"))

print("Patched student_dashboard.html successfully!")
