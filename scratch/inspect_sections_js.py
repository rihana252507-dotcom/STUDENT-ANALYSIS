with open('static/js/app.js', encoding='utf-8') as f:
    lines = f.readlines()

def print_range(start, end):
    print(f"=== Lines {start} to {end} ===")
    for idx in range(start-1, min(end, len(lines))):
        print(f"{idx+1}: {lines[idx].rstrip()}")

print_range(720, 785)
print_range(970, 1030)
print_range(1633, 1720)
