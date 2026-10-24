with open('services/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''                # Redirect user to their own dashboard
                if user_role == "admin":
                    return redirect(url_for("admin_dashboard"))
                elif user_role == "faculty":
                    return redirect(url_for("faculty_dashboard"))
                elif user_role == "student":
                    return redirect(url_for("student_dashboard"))'''

replacement = '''                # Redirect user to their own dashboard
                if user_role == "admin":
                    return redirect(url_for("admin_dashboard"))
                elif user_role == "hod":
                    return redirect(url_for("hod_dashboard"))
                elif user_role == "faculty":
                    return redirect(url_for("faculty_dashboard"))
                elif user_role == "student":
                    return redirect(url_for("student_dashboard"))'''

if target in content:
    content = content.replace(target, replacement, 1)
    with open('services/auth.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated services/auth.py")
else:
    print("Target not found in services/auth.py")
