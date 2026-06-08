import sys
import glob

files = [
    r"d:\study-plan\revision\frontend\day_01.md",
    r"d:\study-plan\revision\frontend\day_02.md"
]

for file_path in files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix the `<br/>` tag issue that breaks markdown rendering in Github Details blocks
        content = content.replace("<br/>\n\n", "\n")
        content = content.replace("<br/>\r\n\r\n", "\n")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed br tags in {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
