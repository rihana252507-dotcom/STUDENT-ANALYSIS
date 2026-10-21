import sqlite3, json

conn = sqlite3.connect('database/campusiq.db')
c = conn.cursor()
c.execute("SELECT student_id, name, cgpa, attendance_pct, backlogs, success_score, placement_aptitude_score, technical_skills_score, risk_level FROM students")
rows = c.fetchall()
print(f"Total students: {len(rows)}")

low_att = []
placement_gap = []
backlogs = []
stars = []
low_risk = []

for r in rows:
    sid, name, cgpa, att, bkl, succ, apt, tech, risk = r
    if att < 75.0:
        low_att.append((sid, name, att))
    if cgpa >= 7.5 and (apt < 65 or tech < 70):
        placement_gap.append((sid, name, cgpa, apt, tech))
    if bkl > 0:
        backlogs.append((sid, name, bkl))
    if (succ or 0) >= 80:
        stars.append((sid, name, succ))
    if risk == 'Low':
        low_risk.append((sid, name, risk, succ))

print("\n1. Low Attendance (<75%):", len(low_att), low_att)
print("\n2. Placement Gap (CGPA>=7.5, apt<65 or tech<70):", len(placement_gap), placement_gap)
print("\n3. Backlogs (>0):", len(backlogs), backlogs)
print("\n4. Stars (Score>=80):", len(stars), stars)
print("\n5. Low Risk:", len(low_risk), low_risk)
conn.close()
