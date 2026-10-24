with open('templates/student_dashboard.html', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="section-attendance"')
end_idx = text.find('</section>', idx) + len('</section>')
print("=== section-attendance (length: {}) ===".format(end_idx - idx))
print(text[idx:end_idx])
