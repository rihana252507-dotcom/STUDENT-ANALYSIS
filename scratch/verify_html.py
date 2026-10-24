with open("STUDENT-ANALYSIS/templates/hod_dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

print("File size:", len(html))
print("Contains modalBacklogsBreakdownSection:", "modalBacklogsBreakdownSection" in html)
print("Contains modalRiskFactorsContainer:", "modalRiskFactorsContainer" in html)
print("Contains modalStrengthsContainer:", "modalStrengthsContainer" in html)
print("Contains studentDetailModal:", "studentDetailModal" in html)
print("Contains loadHodDashboard:", "loadHodDashboard" in html)
print("Contains </script>:", "</script>" in html)
print("Ends with </html>:", html.strip().endswith("</html>"))
