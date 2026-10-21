"""
CampusIQ – Academic Curriculum and Multi-Semester History Generator
Provides calibrated course catalogs and examination telemetry for engineering branches
(CSE, IT, AI&DS, ECE, ME) across Years 1 to 4 (Semesters 1-1 to 4-2).
"""

CURRICULUM = {
    "COMMON_YEAR_1": {
        1: [ # 1-1
            ("MATH101", "Linear Algebra & Advanced Calculus", 4),
            ("PHYS101", "Applied Engineering Physics", 4),
            ("CS101", "Problem Solving & C Programming", 3),
            ("EE101", "Basic Electrical Engineering", 3),
            ("ME101", "Engineering Graphics & Design", 2),
            ("CS101L", "C Programming & Problem Solving Lab", 1.5)
        ],
        2: [ # 1-2
            ("MATH102", "Differential Equations & Numerical Methods", 4),
            ("CHEM102", "Engineering Chemistry & Materials", 3),
            ("CS102", "Data Structures & Algorithms in C/C++", 4),
            ("EC102", "Basic Electronic Devices & Sensors", 3),
            ("ENG102", "Technical & Professional Communication", 2),
            ("CS102L", "Data Structures Laboratory", 1.5)
        ]
    },
    "CSE": {
        3: [ # 2-1
            ("CS201", "Discrete Mathematical Structures", 4),
            ("CS202", "Digital Logic & Computer Organization", 4),
            ("CS203", "Object-Oriented Programming with Java", 3),
            ("CS204", "Database Management Systems", 4),
            ("CS205", "Python for Computational Problem Solving", 3)
        ],
        4: [ # 2-2
            ("CS206", "Design & Analysis of Algorithms", 4),
            ("CS207", "Operating Systems & Kernel Concepts", 4),
            ("CS208", "Software Engineering & Agile Methodologies", 3),
            ("CS209", "Formal Languages & Automata Theory", 3),
            ("MATH202", "Probability & Statistics for Engineers", 3)
        ],
        5: [ # 3-1
            ("CS301", "Computer Networks & Distributed Protocols", 4),
            ("CS302", "Web Technologies & Full-Stack Development", 4),
            ("CS303", "Compiler Design & Code Generation", 4),
            ("CS304", "Artificial Intelligence & Expert Systems", 3),
            ("CS305", "Cloud Computing Foundations & Virtualization", 3)
        ],
        6: [ # 3-2
            ("CS306", "Machine Learning & Pattern Recognition", 4),
            ("CS307", "Cryptography & Information Security", 4),
            ("CS308", "Big Data Analytics & Distributed Systems", 3),
            ("CS309", "Mobile Application Architecture", 3),
            ("OE301", "Open Elective: Renewable Energy & Sustainability", 3)
        ],
        7: [ # 4-1
            ("CS401", "Deep Learning & Neural Architectures", 4),
            ("CS402", "DevOps & Continuous Deployment Pipelines", 3),
            ("CS403", "Distributed Systems & Microservices", 3),
            ("PROJ401", "Capstone Major Project Phase-I", 4)
        ],
        8: [ # 4-2
            ("T&P201", "KPMG Campus Placement Mock Aptitude & Coding", 2),
            ("CS404", "Cloud Security, Identity & Governance", 3),
            ("PROJ402", "Capstone Major Project Phase-II", 6)
        ]
    },
    "IT": {
        3: [ # 2-1
            ("IT201", "Data Structures & Algorithmic Problem Solving", 4),
            ("IT202", "Digital Principles & System Architecture", 4),
            ("IT203", "Object-Oriented Programming via Java", 3),
            ("IT204", "Relational Database Management Systems", 4),
            ("IT205", "Computer Architecture & Organization", 3)
        ],
        4: [ # 2-2
            ("IT206", "Design & Analysis of Algorithms", 4),
            ("IT207", "Operating Systems & Linux Shell Programming", 4),
            ("IT208", "Object-Oriented Software Engineering", 3),
            ("IT209", "Information Theory & Data Coding", 3),
            ("MATH202", "Probability & Statistics for Engineers", 3)
        ],
        5: [ # 3-1
            ("IT301", "Computer Communication Networks", 4),
            ("IT302", "Full-Stack Web Development & APIs", 4),
            ("IT303", "Cloud Computing & DevOps Pipelines", 3),
            ("IT304", "Information Security & Cryptography", 3),
            ("IT305", "Data Mining & Business Intelligence", 3)
        ],
        6: [ # 3-2
            ("IT306", "Mobile Computing & Wireless Systems", 4),
            ("IT307", "Network Security & Cyber Forensics", 4),
            ("IT308", "Big Data Technologies & Analytics", 3),
            ("IT309", "Human-Computer Interaction & UI/UX", 3),
            ("OE301", "Open Elective: Innovation & Tech Entrepreneurship", 3)
        ],
        7: [
            ("IT401", "Enterprise Cloud Architecture", 4),
            ("IT402", "Software Quality Assurance & Testing", 3),
            ("PROJ401", "Capstone Major Project Phase-I", 4)
        ],
        8: [
            ("T&P201", "KPMG Campus Placement Mock Aptitude & Coding", 2),
            ("PROJ402", "Capstone Major Project Phase-II", 6)
        ]
    },
    "AI&DS": {
        3: [ # 2-1
            ("AIDS201", "Python for Data Science & Machine Learning", 4),
            ("AIDS202", "Data Structures & Algorithms in Python", 4),
            ("AIDS203", "Linear Algebra for Machine Learning", 3),
            ("AIDS204", "RDBMS & NoSQL Distributed Databases", 4),
            ("AIDS205", "Discrete Mathematics for Computing", 3)
        ],
        4: [ # 2-2
            ("AIDS206", "Design & Analysis of Algorithms", 4),
            ("AIDS207", "Operating Systems & Systems Programming", 4),
            ("AIDS208", "Exploratory Data Analysis & Visualization", 3),
            ("AIDS209", "Probability, Random Variables & Statistics", 3),
            ("AIDS401", "Machine Learning & Predictive Intelligence", 4)
        ],
        5: [
            ("AIDS301", "Deep Learning & Artificial Neural Networks", 4),
            ("AIDS302", "Natural Language Processing & LLMs", 4),
            ("AIDS303", "Big Data Engineering with Hadoop & Spark", 4),
            ("AIDS304", "Cloud Infrastructure for AI Workloads", 3)
        ],
        6: [
            ("AIDS305", "Computer Vision & Image Analytics", 4),
            ("AIDS306", "Reinforcement Learning & Decision Systems", 4),
            ("AIDS307", "AI Ethics, Governance & Model Safety", 3),
            ("OE301", "Open Elective: Quantum Computing Basics", 3)
        ]
    },
    "AIML": {
        3: [ # 2-1
            ("AIML201", "Python for Machine Learning & Scientific Computing", 4),
            ("AIML202", "Data Structures & Algorithmic Problem Solving", 4),
            ("AIML203", "Linear Algebra & Optimization for AI", 3),
            ("AIML204", "Database Systems & Feature Stores", 4),
            ("AIML205", "Discrete Mathematics & Logic for AI", 3)
        ],
        4: [ # 2-2
            ("AIML206", "Design & Analysis of Machine Learning Algorithms", 4),
            ("AIML207", "Operating Systems & High Performance Computing", 4),
            ("AIML208", "Probability, Random Variables & Bayesian Statistics", 3),
            ("AIML209", "Exploratory Data Analysis & Dimensionality Reduction", 3),
            ("AIML401", "Artificial Intelligence and Machine Learning", 4)
        ],
        5: [ # 3-1
            ("AIML301", "Deep Learning & Artificial Neural Networks", 4),
            ("AIML302", "Natural Language Processing & Transformers", 4),
            ("AIML303", "Computer Vision & Visual Pattern Recognition", 4),
            ("AIML304", "MLOps & Cloud Infrastructure for AI Systems", 3)
        ],
        6: [ # 3-2
            ("AIML305", "Reinforcement Learning & Decision Intelligence", 4),
            ("AIML306", "Generative AI & Large Language Models", 4),
            ("AIML307", "AI Safety, Interpretability & Algorithmic Ethics", 3),
            ("OE301", "Open Elective: Quantum Computing Basics", 3)
        ]
    },
    "ECE": {
        3: [ # 2-1
            ("EC201", "Signals, Systems & Transform Techniques", 4),
            ("EC202", "Electronic Circuit Analysis & Design", 4),
            ("EC203", "Digital Logic Design & Verilog HDL", 4),
            ("EC204", "Network Analysis & Transmission Lines", 3),
            ("MATH201", "Complex Variables & Vector Calculus", 3)
        ],
        4: [ # 2-2
            ("EC205", "Analog & Digital Communication Systems", 4),
            ("EC206", "Electromagnetic Fields & Wave Propagation", 4),
            ("EC207", "Linear Integrated Circuits & Applications", 3),
            ("EC208", "Pulse, Digital & Switching Circuits", 3),
            ("CS210", "Data Structures & C++ for Electronics", 3)
        ],
        5: [ # 3-1
            ("EC301", "Microprocessors, ARM & Microcontrollers", 4),
            ("EC302", "Digital Signal Processing & Architectures", 4),
            ("EC303", "Digital Communication Protocols & Cellular", 4),
            ("EC304", "Antennas & Microwave Propagation", 3),
            ("EC305", "Control Systems Engineering & State Models", 3)
        ],
        6: [ # 3-2
            ("ECE304", "Digital Signal Processing & Microcontrollers", 4),
            ("EC306", "VLSI System Design & CMOS Technology", 4),
            ("EC307", "Microwave Engineering & Radar Systems", 3),
            ("EC308", "Embedded IoT Systems & RTOS", 3),
            ("OE301", "Open Elective: Biomedical Instrumentation", 3)
        ]
    },
    "ME": {
        3: [ # 2-1
            ("ME201", "Engineering Mechanics, Statics & Dynamics", 4),
            ("ME202", "Engineering Thermodynamics & Gas Cycles", 4),
            ("ME203", "Metallurgy, Materials Science & Testing", 3),
            ("ME204", "Mechanics of Solids & Strength of Materials", 4),
            ("MATH201", "Partial Differential Equations & Transforms", 3)
        ],
        4: [ # 2-2
            ("ME205", "Fluid Mechanics & Hydraulic Machinery", 4),
            ("ME206", "Kinematics of Machinery & Mechanism Design", 4),
            ("ME207", "Manufacturing Processes, Casting & Welding", 3),
            ("ME208", "Thermal Engineering & IC Engines", 4),
            ("EE209", "Electrical Drives & Microcontroller Control", 3)
        ],
        5: [ # 3-1
            ("ME301", "Applied Thermodynamics & Fluid Mechanics", 4),
            ("ME302", "Dynamics of Machinery & Mechanical Vibrations", 4),
            ("ME303", "Design of Machine Elements & Fatigue", 4),
            ("ME304", "Machining Science & Machine Tools", 3),
            ("ME305", "Operations Research & Production Planning", 3)
        ],
        6: [ # 3-2
            ("ME306", "Heat & Mass Transfer Engineering", 4),
            ("ME307", "Finite Element Analysis (FEA) & Simulation", 4),
            ("ME308", "CAD/CAM & Industrial Robotics", 3),
            ("ME309", "Automobile Systems & Hybrid Vehicles", 3),
            ("OE301", "Open Elective: Supply Chain Logistics", 3)
        ]
    }
}

ACADEMIC_YEARS = {
    1: "2022-2023",
    2: "2022-2023",
    3: "2023-2024",
    4: "2023-2024",
    5: "2024-2025",
    6: "2024-2025",
    7: "2025-2026",
    8: "2025-2026"
}

# Specific backlog assignments matching students.csv exactly
BACKLOG_ASSIGNMENTS = {
    "CIQ-2026-004": [("AIDS203", 3)], # Ananya Gupta: 1 backlog in Sem 3
    "CIQ-2026-006": [("IT206", 4)],   # Sneha Patel: 1 backlog in Sem 4
    "CIQ-2026-007": [("IT207", 4), ("IT301", 5)], # Divya Rao: 2 backlogs
    "CIQ-2026-008": [("CS102", 2), ("CS202", 3), ("CS206", 4)], # Kabir Mehta: 3 backlogs
    "CIQ-2026-009": [("EC201", 3), ("EC206", 4)], # Pooja Nair: 2 backlogs
    "CIQ-2026-010": [("ME202", 3), ("ME206", 4)]  # Arjun Verma: 2 backlogs
}

def generate_records_for_student(student):
    """
    Generates deterministic academic records for a given student row
    matching their department, completed semesters, CGPA, and backlog count.
    """
    student_id = student["student_id"]
    dept = student["department"]
    current_sem = int(student["semester"])
    cgpa = float(student["cgpa"])
    target_marks = float(student["academic_marks_pct"])
    student_att = float(student["attendance_pct"])
    backlog_codes = dict(BACKLOG_ASSIGNMENTS.get(student_id, []))

    records = []

    for sem in range(1, current_sem + 1):
        year_num = (sem + 1) // 2
        sem_part = 1 if (sem % 2 != 0) else 2
        sem_label = f"{year_num}-{sem_part}"
        acad_year = ACADEMIC_YEARS.get(sem, "2024-2025")

        # Select courses
        if sem in [1, 2]:
            courses = CURRICULUM["COMMON_YEAR_1"].get(sem, [])
        else:
            dept_curric = CURRICULUM.get(dept, CURRICULUM["CSE"])
            courses = dept_curric.get(sem, CURRICULUM["CSE"].get(sem, []))

        sem_records = []
        sem_weighted_pts = 0.0
        sem_total_credits = 0

        for c_idx, (c_code, c_name, credits) in enumerate(courses):
            is_backlog = (c_code in backlog_codes and backlog_codes[c_code] == sem)

            if is_backlog:
                # Failed / Backlog Subject
                mid1 = round(6.0 + (c_idx % 3) * 1.5, 1)
                mid2 = round(7.0 + (c_idx % 2) * 1.0, 1)
                internal = round(mid1 + mid2, 1) # out of 40
                external = round(14.0 + (c_idx % 4) * 1.5, 1) # out of 60
                total = round(internal + external, 1)
                grade = "F"
                status = "Backlog"
                grade_point = 0.0
                classes_conducted = 46
                classes_attended = max(18, int(classes_conducted * (student_att / 100.0) - 8))
            else:
                # Passed Subject calibrated to CGPA & marks_pct
                # Variations per subject (+/- 4 pts)
                variance = ((c_idx * 37) % 9) - 4
                base_pct = max(45.0, min(97.0, target_marks + variance))

                # Mid exams (20 max each)
                mid1 = round(min(20.0, max(8.0, (base_pct / 100.0) * 20.0 + ((c_idx % 3) - 1) * 0.5)), 1)
                mid2 = round(min(20.0, max(8.0, (base_pct / 100.0) * 20.0 + ((c_idx % 2) - 0.5) * 0.5)), 1)
                internal = round(mid1 + mid2, 1) # out of 40
                external = round(min(60.0, max(24.0, (base_pct / 100.0) * 60.0)), 1) # out of 60
                total = round(internal + external, 1)

                if total >= 90:
                    grade = "O"
                    grade_point = 10.0
                elif total >= 80:
                    grade = "A+"
                    grade_point = 9.0
                elif total >= 70:
                    grade = "A"
                    grade_point = 8.0
                elif total >= 60:
                    grade = "B+"
                    grade_point = 7.0
                elif total >= 50:
                    grade = "B"
                    grade_point = 6.0
                elif total >= 40:
                    grade = "C"
                    grade_point = 5.0
                else:
                    grade = "F"
                    grade_point = 0.0

                status = "Passed" if grade != "F" else "Backlog"
                classes_conducted = 48
                classes_attended = min(classes_conducted, max(20, int(classes_conducted * (student_att / 100.0) + ((c_idx % 3) - 1))))

            att_pct = round((classes_attended / classes_conducted) * 100.0, 1)

            sem_weighted_pts += (grade_point * credits)
            sem_total_credits += credits

            sem_records.append({
                "student_id": student_id,
                "year": year_num,
                "semester": sem,
                "semester_label": sem_label,
                "academic_year": acad_year,
                "course_code": c_code,
                "course_name": c_name,
                "credits": credits,
                "mid1_marks": mid1,
                "mid1_max": 20.0,
                "mid2_marks": mid2,
                "mid2_max": 20.0,
                "internal_marks": internal,
                "internal_max": 40.0,
                "external_marks": external,
                "external_max": 60.0,
                "total_marks": total,
                "total_max": 100.0,
                "grade": grade,
                "status": status,
                "classes_conducted": classes_conducted,
                "classes_attended": classes_attended,
                "attendance_pct": att_pct
            })

        # Calculate SGPA for semester
        sem_sgpa = round(sem_weighted_pts / sem_total_credits, 2) if sem_total_credits > 0 else 0.0
        for rec in sem_records:
            rec["sgpa"] = sem_sgpa
            records.append(rec)

    return records
