with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add dashboard aliases
if '@app.route("/admin/dashboard")' not in content:
    content = content.replace(
        '@app.route("/admin")\n',
        '@app.route("/admin")\n@app.route("/admin/dashboard")\n'
    )
    print("Added /admin/dashboard alias")

if '@app.route("/faculty/dashboard")' not in content:
    content = content.replace(
        '@app.route("/faculty")\n',
        '@app.route("/faculty")\n@app.route("/faculty/dashboard")\n'
    )
    print("Added /faculty/dashboard alias")

if '@app.route("/student/dashboard")' not in content:
    content = content.replace(
        '@app.route("/student")\n',
        '@app.route("/student")\n@app.route("/student/dashboard")\n'
    )
    print("Added /student/dashboard alias")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py dashboard routes successfully")
