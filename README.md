# Canvas Autograder

A simple tool that automatically grades Canvas assignment submissions based on word count. It reads your submissions folder and grades CSV, then produces an updated CSV file ready to upload back to Canvas.

---

## What This Does

The autograder checks each student's submission (PDF, HTML, or Word document) and counts the words. If the submission has **200 or more words**, the student gets full credit (100). If it has **fewer than 200 words**, they get partial credit (50). Late submissions (filenames with `LATE` between the first and second underscore) receive a 25-point penalty. Students who did not submit get a 0. Students with **EX** (excused) in the grade column are skipped and their grade is left unchanged. You can change these numbers if you want different rules (see [Changing the Grading Rules](#changing-the-grading-rules) below).

---

## Prerequisites

You need **Python** installed on your computer. Python 3.8 or newer is required.

- **Don't have Python?** Download it from [python.org](https://www.python.org/downloads/). During installation, check the box that says "Add Python to PATH."
- **Not sure if you have it?** Open Command Prompt or PowerShell and type `python --version`. If you see a version number (e.g., `Python 3.12.0`), you're good.

---

## Setup

1. **Put your files in the right place**
   - Place your Canvas **grades CSV file** in the `input` folder.
   - Place all **submissions** in the `input/submissions` folder.
   - The repo includes example files (`example_Grades.csv` and sample submissions) so you can try it immediately. Replace these with your real data when grading.

   Your folder structure should look like this:
   ```
   canvas autograder/
   ├── autograder.py
   ├── input/
   │   ├── 2026-02-16T1430_Grades-MTDE-252_500,MTDE-652_601.csv   (your grades CSV)
   │   └── submissions/
   │       ├── student1_123456_text.html
   │       ├── student2_789012_document.pdf
   │       ├── student3_LATE_123789_reflection.docx   (late = 25 pt penalty)
   │       └── ...
   └── output/   (created automatically; graded CSV goes here)
   ```

2. **Install the required tools**
   - Open Command Prompt or PowerShell.
   - Go to the folder where `autograder.py` lives. For example:
     ```
     cd "C:\Projects\Coding\We_Can_Do_It\canvas autograder"
     ```
   - Run:
     ```
     pip install -r requirements.txt
     ```
   - Wait for it to finish. You only need to do this once.

---

## How to Run

1. Open Command Prompt or PowerShell.
2. Go to the folder with `autograder.py`:
   ```
   cd "C:\Projects\Coding\We_Can_Do_It\canvas autograder"
   ```
3. Run:
   ```
   python autograder.py
   ```
4. **Choose the assignment:** Use the **Up** and **Down** arrow keys to select which Weekly Reflection assignment you're grading, then press **Enter**.

5. The script will process each submission and show you the results. When it's done, it will tell you where the new CSV file was saved.

---

## Changing the Grading Rules

Open `autograder.py` in a text editor (e.g., Notepad, VS Code). Near the top of the file, you'll see a section that looks like this:

```python
# ============ GRADING THRESHOLDS - CUSTOMIZE THESE ============
WORD_COUNT_THRESHOLD = 200   # Minimum words for full credit
SCORE_PASS = 100             # Score when word count >= threshold
SCORE_FAIL = 50              # Score when word count < threshold
LATE_PENALTY = 25            # Points subtracted for late submissions
# ==============================================================
```

- **WORD_COUNT_THRESHOLD:** Change `200` to whatever minimum word count you want for full credit.
- **SCORE_PASS:** Change `100` to the score students get when they meet the word count.
- **SCORE_FAIL:** Change `50` to the score students get when they don't meet the word count.
- **LATE_PENALTY:** Change `25` to the points subtracted for late submissions (filenames with `LATE` between the first and second underscore, e.g. `username_LATE_123456_file.pdf`).

Save the file after making changes.

---

## Output

The script creates a **new** CSV file—it does not overwrite your original. The new file is named like your original file with `_graded` added, for example:

- Original (in `input/`): `2026-02-16T1430_Grades-MTDE-252_500,MTDE-652_601.csv`
- Output (in `output/`): `2026-02-16T1430_Grades-MTDE-252_500,MTDE-652_601_graded.csv`

The output file is saved in the `output` folder. Upload this file to Canvas to update the grades.

---

## Troubleshooting

### "No module named 'questionary'" (or similar)

You need to install the required tools. Run:

```
pip install -r requirements.txt
```

from the folder that contains `autograder.py`.

---

### "CSV not found" or "Submissions folder not found"

- Put your grades CSV (the file that starts with a date and contains "Grades") in the `input` folder.
- Put all student submissions in the `input/submissions` folder.

---

### DOCX or PDF not reading correctly

- **DOCX:** The script uses the first paragraph it finds. If the document has unusual formatting or is mostly images, it may not count words correctly.
- **PDF:** The script reads text from the PDF. If the PDF is a scanned image (no selectable text), the script cannot read it. You would need OCR software to convert it to text first.

---

### Arrow keys don't work in the assignment menu

Make sure you're running the script in a normal Command Prompt or PowerShell window, not inside some editors or special environments. The arrow-key menu needs a real terminal.

---

## Supported File Types

- **PDF** (`.pdf`)
- **HTML** (`.html`, `.htm`) — text is taken from `<p>` (paragraph) tags
- **Word** (`.docx`)

Submissions must follow the Canvas naming pattern: `username_ID_...` where the student ID is between the first and second underscore. For late submissions, use `username_LATE_ID_...` (ID between the second and third underscore); these receive a 25-point penalty.
