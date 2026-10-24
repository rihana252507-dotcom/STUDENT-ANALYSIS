with open('database/db.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '        mentor_map = {'
insertion = '''        # -------------------------------------------------------------
        # SEED 4b: HOD (HEAD OF DEPARTMENT) ACCOUNTS
        # -------------------------------------------------------------
        hod_data = [
            ("hod_cse", "Hod@123", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
            ("hod_aiml", "Hod@123", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
            ("hod_ece", "Hod@123", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
            ("hod_it", "Hod@123", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
        ]
        for h_user, h_pass, h_name, h_email, h_dept in hod_data:
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_id = ?", (h_user,))
            if cursor.fetchone()["count"] == 0:
                h_pass_hash = generate_password_hash(h_pass)
                cursor.execute("""
                INSERT INTO users (user_id, password_hash, role, name, email, department)
                VALUES (?, ?, 'hod', ?, ?, ?)
                """, (h_user, h_pass_hash, h_name, h_email, h_dept))

        mentor_map = {'''

if target in content and 'SEED 4b: HOD' not in content:
    content = content.replace(target, insertion, 1)
    with open('database/db.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added HOD seed to database/db.py")
else:
    print("Already added or target not found")
