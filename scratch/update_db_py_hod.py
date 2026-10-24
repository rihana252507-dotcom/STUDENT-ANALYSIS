import os

db_py_path = os.path.join(os.path.dirname(__file__), "..", "database", "db.py")
with open(db_py_path, "r", encoding="utf-8") as f:
    text = f.read()

norm_text = text.replace("\r\n", "\n")

old_hod = """        hod_data = [
            ("hod_cse", "Hod@123", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
            ("hod_aiml", "Hod@123", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
            ("hod_ece", "Hod@123", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
            ("hod_it", "Hod@123", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
        ]"""

new_hod = """        hod_data = [
            ("hod_cse", "Hod@123", "Dr. Sunita Rao (HOD CSE)", "hod.cse@campusiq.edu", "CSE"),
            ("hod_aiml", "Hod@123", "Dr. Priya Krishnaswamy (HOD AIML)", "hod.aiml@campusiq.edu", "AIML"),
            ("hod_ece", "Hod@123", "Dr. Amit Verma (HOD ECE)", "hod.ece@campusiq.edu", "ECE"),
            ("hod_it", "Hod@123", "Dr. Meenakshi Sundaram (HOD IT)", "hod.it@campusiq.edu", "IT"),
            ("hod_aids", "Hod@123", "Prof. Neha Gupta (HOD AI&DS)", "hod.aids@campusiq.edu", "AI&DS"),
            ("hod_me", "Hod@123", "Dr. K. S. Pillai (HOD ME)", "hod.me@campusiq.edu", "ME"),
        ]"""

assert old_hod in norm_text, "old_hod not found in db.py"
norm_text = norm_text.replace(old_hod, new_hod, 1)

with open(db_py_path, "wb") as f:
    f.write(norm_text.replace("\n", "\r\n").encode("utf-8"))

print("Updated database/db.py successfully!")
