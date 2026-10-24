with open('frontend/script.js', 'r', encoding='utf-8') as f:
    front_js = f.read()

target = 'const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\\n");'
repl = 'const csvContent = "data:text/csv;charset=utf-8,\\ufeff" + [headers.join(","), ...rows.map(r => r.join(","))].join("\\n");'

if target in front_js:
    front_js = front_js.replace(target, repl, 1)
    with open('frontend/script.js', 'w', encoding='utf-8') as f:
        f.write(front_js)
    print("SUCCESS: frontend/script.js updated with UTF-8 BOM!")
else:
    print("WARNING: target not found in frontend/script.js")
