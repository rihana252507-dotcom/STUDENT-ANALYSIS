# CampusIQ – AI-Powered Student Analytics & Success Platform
### KPMG in India HacXLerate 2026 Hackathon Challenge Prototype

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%203-003B57.svg)](https://www.sqlite.org/)
[![Charts](https://img.shields.io/badge/Charts-Chart.js%20v4-FF6384.svg)](https://www.chartjs.org/)
[![Security](https://img.shields.io/badge/Security-PBKDF2%20Hashed%20Sessions-success.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-10%20Calibrated%20Students-green.svg)]()
[![Theme](https://img.shields.io/badge/Theme-Electric%20Purple%20%26%20Vibrant%20Pink%20Glassmorphism-purple.svg)]()

---

## 📌 Executive Summary

**CampusIQ** is a full-stack, enterprise-grade AI-powered Student Analytics and Early Risk Intervention Platform built specifically for the **KPMG in India HacXLerate 2026 Hackathon Challenge**. Engineered as a single, unified full-stack application (Python Flask, SQLite, and vanilla HTML/CSS/JavaScript with Chart.js), CampusIQ transforms fragmented institutional data—academic marks, CGPA, biometric attendance, backlogs, LMS engagement, assignment completion, placement aptitude, technical coding skills, and student wellbeing feedback—into explainable, actionable intelligence.

### Design Theme
CampusIQ features a visual design system built around **electric purple (`#8B5CF6`)**, **vibrant pink (`#EC4899`, `#F43F5E`)**, **soft lilac (`#C4B5FD`)**, **lavender (`#E9D5FF`)**, and **deep violet (`#0B061A`, `#12092B`)**. It incorporates modern glassmorphism panels, glowing KPI scorecards, smooth transitions, collapsible quick-demo credentials, and responsive sidebars with **zero dead links**.

---

## 🏢 Mandatory Demo Accounts & Credentials

The platform features an automated SQLite database engine and seed generator. All requested demo accounts are pre-seeded with secure PBKDF2 password hashing:

| Role | User ID / Username | Password | Identity & Context |
|---|---|---|---|
| **Admin** | `admin001` | `Admin@123` | Dr. V. Ramanathan (Dean of Academics) |
| **Faculty 1** | `faculty001` | `Faculty@123` | Dr. Sunita Rao (Professor & Head, CSE) |
| **Student 1** | `student001` | `Student@123` | Aarav Reddy (CSE, Sem 8 &bull; 92.3 Success Score &bull; Low Risk) |
| **Faculty 2** | `faculty002` | `Faculty@123` | Dr. Meenakshi Sundaram (Professor & Head, IT) |
| **Student 2** | `student002` | `Student@123` | Aditi Kulkarni (IT, Sem 6 &bull; 87.2 Success Score &bull; Low Risk) |
| **High-Risk Demo** | `student008` | `Student@123` | Kabir Mehta (IT, Sem 6 &bull; 37.5 Success Score &bull; High Risk) |

*(A collapsible Quick Demo Access card is available directly on the login screen with 1-click credential auto-fill).*

---

## 📊 Calibrated 10-Student Demonstration Cohort

To facilitate transparent and rigorous hackathon judging, CampusIQ includes **exactly 10 realistic dummy student records** (`data/students.csv`). Every count, percentage, chart, and alert in the dashboard derives dynamically from SQLite and the rule-based scoring engine:

* **Low-Risk Cohort (2 Students — 20.0%)**:
  - `CIQ-2026-001` (`student001`): Aarav Reddy (CSE) — CGPA 9.35, Attendance 94.0%, 0 Backlogs &bull; **Score: 92.3**
  - `CIQ-2026-002` (`student002`): Aditi Kulkarni (IT) — CGPA 8.85, Attendance 89.0%, 0 Backlogs &bull; **Score: 87.2**
* **Medium-Risk Cohort (4 Students — 40.0%)**:
  - `CIQ-2026-003` (`student003`): Rohan Sharma (CSE) — CGPA 8.40, Attendance 82.0%, 0 Backlogs &bull; **Score: 72.8** (Academically Strong but Placement-Unready)
  - `CIQ-2026-004` (`student004`): Ananya Gupta (ECE) — CGPA 7.45, Attendance 78.5%, 1 Backlog &bull; **Score: 68.8** (Academic Velocity & Backlog Risk)
  - `CIQ-2026-005` (`student005`): Vikram Malhotra (ME) — CGPA 7.10, Attendance 76.0%, 0 Backlogs &bull; **Score: 66.6** (Balanced Steady Performer)
  - `CIQ-2026-006` (`student006`): Sneha Patel (AI&DS) — CGPA 6.95, Attendance 77.0%, 1 Backlog &bull; **Score: 64.9** (Academic Velocity & Backlog Risk)
* **High-Risk Cohort (4 Students — 40.0%)**:
  - `CIQ-2026-007` (`student007`): Divya Rao (IT) — CGPA 5.80, Attendance 61.5%, 2 Backlogs &bull; **Score: 41.5** (Low Attendance & Debarment Risk)
  - `CIQ-2026-008` (`student008`): Kabir Mehta (IT) — CGPA 5.40, Attendance 68.0%, 3 Backlogs &bull; **Score: 37.5** (Low Attendance & Debarment Risk)
  - `CIQ-2026-009` (`student009`): Pooja Nair (ECE) — CGPA 5.20, Attendance 58.0%, 2 Backlogs &bull; **Score: 36.8** (Low Attendance & Debarment Risk)
  - `CIQ-2026-010` (`student010`): Arjun Verma (CSE) — CGPA 5.60, Attendance 65.0%, 2 Backlogs &bull; **Score: 36.2** (Low Attendance & Debarment Risk)

---

## 🚀 Three Advanced Role Dashboards

### 1. Admin Dashboard (`/admin`)
* **Navigation (Exact 9 Items + Logout):**
  1. Overview (`section-overview`)
  2. Students (`section-students`)
  3. Faculty (`section-faculty`)
  4. Risk Monitoring (`section-risk-monitoring`)
  5. AI Insights (`section-ai-insights`)
  6. Interventions (`section-interventions`)
  7. Placement Analytics (`section-placement`)
  8. Reports (`section-reports`)
  9. Settings (`section-settings`)
  10. Logout
* **Features:** Macro institutional KPIs (10 Students, 5 Faculty, 5 Departments, 7 Courses), Chart.js visualizations (Risk Doughnut, Department Benchmarks, Attendance vs CGPA Scatter, Systemic Risk Drivers), Add/Edit/Delete Student modals, Add Faculty modal, What-If Academic Simulator, and dynamic CSV report export.

### 2. Faculty Dashboard (`/faculty`)
* **Navigation (Exact 7 Items + Logout):**
  1. Overview (`section-overview`)
  2. My Students (`section-my-students`)
  3. Academic Performance (`section-academic-performance`)
  4. Risk Alerts (`section-risk-alerts`)
  5. Student Profiles (`section-student-profiles`)
  6. Interventions (`section-interventions`)
  7. Reports (`section-reports`)
  8. Logout
* **Features:** Direct advisee caseload tracking, instant search and risk filtering, 1-click intervention logging with SQLite persistence (`Pending`, `In Progress`, `Completed`), counseling minutes recording, and statutory attendance alerts.

### 3. Student Dashboard (`/student`)
* **Navigation (Exact 8 Items + Logout):**
  1. My Dashboard (`section-my-dashboard`)
  2. My Academics (`section-my-academics`)
  3. Attendance (`section-attendance`)
  4. My Success Score (`section-my-success-score`)
  5. Placement Readiness (`section-placement-readiness`)
  6. Recommendations (`section-personalized-recommendations`)
  7. Notifications (`section-notifications`)
  8. Profile (`section-my-profile`)
  9. Logout
* **Features:** Personalized welcome header, composite success score and risk badge, 5-Pillar radar chart, course-by-course marks and grade predictions, biometric attendance tracking with statutory 75% cutoff indicator, verified technical skill badges, explainable factor attribution, tailored academic roadmap, and interactive personal What-If Simulator.
* **Privacy Boundary:** Server-side role authorization strictly prevents students from viewing or simulating data belonging to other students (`403 Forbidden`).

---

## 🧠 Explainable AI Analytics Engine (5 Pillars)

CampusIQ explicitly avoids opaque black-box claims. It computes an explainable, deterministic **Student Success Score (0–100)**:

$$\text{Success Score} = 0.30 \cdot P_{\text{Academic}} + 0.20 \cdot P_{\text{Attendance}} + 0.15 \cdot P_{\text{LMS}} + 0.20 \cdot P_{\text{Placement}} + 0.15 \cdot P_{\text{Wellbeing}}$$

1. **Academic Mastery (30% weight)**: Normalized CGPA (60%) + Internal Exam Marks (40%) with an explicit penalty of $-12$ points per active backlog.
2. **Attendance & Discipline (20% weight)**: Direct biometric attendance if $\ge 75\%$; non-linear penalty for deficits below statutory $75\%$ ($1.5 \times$ shortfall deduction).
3. **LMS & Digital Engagement (15% weight)**: Normalized weekly learning hours (30%) + engagement index (35%) + assignment submission rate (35%).
4. **Placement Readiness (20% weight)**: Technical coding & DSA assessments (55%) + quantitative/logical aptitude benchmark (45%).
5. **Holistic Wellbeing (15% weight)**: Extracurricular and hackathon participation (55%) + pulse feedback/stress index (45%).

### Risk Classification Thresholds:
* **Low Risk ($\ge 80.0$)**: Excellent academic standing and placement-ready.
* **Medium Risk ($60.0 \le \text{Score} < 80.0$)**: Monitored watchlist for single-factor deficits (e.g. skills gap or 1 backlog).
* **High Risk ($< 60.0$)**: Critical intervention required due to attendance deficit below $75\%$ or multiple active backlogs.

---

## ⏱️ 60-Second Judge Demonstration Walkthrough

When presenting to KPMG hackathon judges, follow this concise flow:

1. **Sign In (10s)**:
   - Go to `http://127.0.0.1:5000/login`. Click **Admin** in the collapsible Quick Demo Access card to auto-fill `admin001` / `Admin@123`, then click **Sign In**.
2. **Institutional Overview & Risk Radar (15s)**:
   - Point out the calibrated KPIs: **10 Students**, **4 High Risk (40%)**, **4 Medium Risk (40%)**, **2 Low Risk (20%)**, 5 Faculty, 5 Departments.
   - Point out the interactive Chart.js widgets (Risk Doughnut, Department Benchmarks, Attendance vs CGPA Scatter).
3. **Explainable AI Attribution & What-If Simulator (20s)**:
   - Click **What-If Simulator** in the top bar. Select `CIQ-2026-008` (Kabir Mehta, baseline score 37.5 High Risk).
   - Increase attendance by $+20\%$ and clear 2 backlogs: watch the score dynamically jump to **51.9** with live factor attribution.
4. **Faculty Intervention Workflow (10s)**:
   - Log out and log in as `faculty001` / `Faculty@123`.
   - Open **Interventions**, change an intervention status from `In Progress` to `Completed`, and show that it persists live in SQLite.
5. **Student Self-Service & Privacy (5s)**:
   - Log out and log in as `student001` / `Student@123`. Show the 5-Pillar radar chart, statutory attendance indicator, and demonstrate that student access is strictly isolated to their own record.

---

## 🛠️ Installation & Setup (VS Code)

### Prerequisites:
* Python 3.10 or higher
* Modern web browser (Chrome, Edge, Firefox)

### Step 1: Open Project in VS Code
Open VS Code and navigate to the project directory:
```bash
cd "c:\Users\SHAIK Rehana\Downloads\hacxelrate"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database (Pre-Seeded)
```bash
python -c "from database.db import init_db; init_db(force=True)"
```

### Step 4: Run Flask Server
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

### Step 5: Run Full Verification Suite
```bash
python -m scratch.test_full_suite
```
All tests verify role authentication, 10-student calibrated distribution, role authorization boundaries, simulation endpoints, and SQLite persistence.
