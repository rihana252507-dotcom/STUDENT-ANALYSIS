with open("STUDENT-ANALYSIS/app.py", "rb") as f:
    raw = f.read()

fixed = raw.replace(b"\r\r\n", b"\r\n")
print(f"Fixed: before {len(raw)} bytes, after {len(fixed)} bytes")
print("Remaining CRCRLF:", fixed.count(b"\r\r\n"))
print("CRLF count:", fixed.count(b"\r\n"))

with open("STUDENT-ANALYSIS/app.py", "wb") as f:
    f.write(fixed)

print("Saved cleanly formatted app.py!")
