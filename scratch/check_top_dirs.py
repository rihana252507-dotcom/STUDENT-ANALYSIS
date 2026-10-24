import os

print("Top level directories:")
for d in os.listdir('.'):
    if os.path.isdir(d) and d not in ['.git', '__pycache__']:
        print(" -", d)
