#!/usr/bin/env python3
"""
Canvas Autograder - Grades submissions by word count and updates CSV.
"""

import csv
import re
from pathlib import Path

from prompt_toolkit.styles import Style
from questionary import select
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document

# ============ GRADING THRESHOLDS - CUSTOMIZE THESE ============
# These settings control how submissions are scored.
# Edit these values to change the grading rules.
WORD_COUNT_THRESHOLD = 200   # Minimum words for full credit
SCORE_PASS = 100             # Score when word count >= threshold
SCORE_FAIL = 50              # Score when word count < threshold
LATE_PENALTY = 25            # Points subtracted for late submissions
# ==============================================================

ID_COL = 1  # Column index for student ID in CSV
SUPPORTED_EXT = (".pdf", ".html", ".htm", ".docx")
_docx_validated = False


def extract_id_from_filename(filename: str) -> tuple[str, bool] | None:
    """Extract (student_id, is_late) from filename.
    Normal: username_ID_rest -> ID between 1st and 2nd _.
    Late: username_LATE_ID_rest -> ID between 2nd and 3rd _.
    """
    parts = filename.split("_")
    if len(parts) >= 2 and parts[1].upper() == "LATE":
        if len(parts) >= 3:
            return (parts[2], True)
        return None
    if len(parts) >= 2:
        return (parts[1], False)
    return None


def count_words_pdf(path: Path) -> int:
    """Extract text from PDF and return word count."""
    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text_parts.append(t)
    text = " ".join(text_parts)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split()) if text else 0


def count_words_html(path: Path) -> int:
    """Extract text from <p> tags in HTML and return word count."""
    with open(path, encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    paras = soup.find_all("p")
    text = " ".join(p.get_text() for p in paras if p.get_text()).strip()
    return len(text.split()) if text else 0


def count_words_docx(path: Path) -> int:
    """Extract text from DOCX and return word count. Prints first paragraph for validation."""
    global _docx_validated
    doc = Document(path)
    paras = [p.text for p in doc.paragraphs if p.text.strip()]
    if paras and not _docx_validated:
        print("\n[VALIDATION] First DOCX paragraph read successfully:")
        print(f"  >>> {paras[0][:200]}{'...' if len(paras[0]) > 200 else ''}\n")
        _docx_validated = True
    text = " ".join(paras).strip()
    return len(text.split()) if text else 0


def count_words(path: Path) -> int:
    """Extract text and count words based on file extension."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return count_words_pdf(path)
    if ext in (".html", ".htm"):
        return count_words_html(path)
    if ext == ".docx":
        return count_words_docx(path)
    return 0


def get_submissions_by_id(submissions_dir: Path) -> dict[str, tuple[Path, bool]]:
    """Scan submissions folder and return {student_id: (filepath, is_late)}. First file wins per ID."""
    result: dict[str, tuple[Path, bool]] = {}
    for f in submissions_dir.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in SUPPORTED_EXT:
            continue
        parsed = extract_id_from_filename(f.name)
        if parsed and parsed[0] not in result:
            result[parsed[0]] = (f, parsed[1])
    return result


def load_csv(path: Path) -> tuple[list[list[str]], list[str], int]:
    """Load CSV, return (rows, header, id_col_index)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("CSV is empty")
    header = rows[0]
    return rows, header, ID_COL


def get_weekly_reflection_columns(header: list[str]) -> list[tuple[int, str]]:
    """Return [(col_index, col_name), ...] for columns containing 'Weekly Reflection'."""
    return [
        (i, name)
        for i, name in enumerate(header)
        if "Weekly Reflection" in (name or "")
    ]


def main() -> None:
    script_dir = Path(__file__).parent.resolve()
    input_dir = script_dir / "input"
    output_dir = script_dir / "output"

    csv_path = next(input_dir.glob("*Grades*.csv"), None)
    submissions_dir = input_dir / "submissions"

    if not csv_path or not csv_path.exists():
        print(f"CSV not found in {input_dir}. Place your grades CSV in the input folder.")
        return
    if not submissions_dir.exists() or not submissions_dir.is_dir():
        print(f"Submissions folder not found: {submissions_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    rows, header, _ = load_csv(csv_path)
    weekly_cols = get_weekly_reflection_columns(header)
    if not weekly_cols:
        print("No 'Weekly Reflection' columns found in CSV.")
        return

    choices = [f"{name} (column {i})" for i, name in weekly_cols]
    purple_style = Style.from_dict({"highlighted": "fg:#6A0DAD bg:#D4C5F9"})
    choice = select(
        "Which assignment are you grading?",
        choices=choices,
        use_arrow_keys=True,
        style=purple_style,
    ).ask()
    if not choice:
        print("Cancelled.")
        return

    selected_idx = choices.index(choice)
    col_index = weekly_cols[selected_idx][0]
    col_name = weekly_cols[selected_idx][1]
    print(f"\nGrading: {col_name}\n")

    submissions = get_submissions_by_id(submissions_dir)
    if not submissions:
        print("No submissions found in folder.")
        return

    graded_ids: set[str] = set()
    id_to_row: dict[str, int] = {}

    for row_idx, row in enumerate(rows):
        if row_idx < 2:  # header + Points Possible
            continue
        if len(row) <= ID_COL:
            continue
        try:
            sid = str(int(row[ID_COL]))
            id_to_row[sid] = row_idx
        except (ValueError, TypeError):
            continue

    # Helper to check if value is excused (preserve EX)
    def is_excused(row: list[str], col: int) -> bool:
        if col >= len(row):
            return False
        return str(row[col]).strip().upper() == "EX"

    for sid, (filepath, is_late) in submissions.items():
        if sid not in id_to_row:
            print(f"  Skipping {sid}: no matching row in CSV")
            continue

        row_idx = id_to_row[sid]
        if is_excused(rows[row_idx], col_index):
            print(f"  Skipping {sid}: excused (EX)")
            graded_ids.add(sid)  # Don't treat as non-submitter
            continue

        word_count = count_words(filepath)
        score = SCORE_PASS if word_count >= WORD_COUNT_THRESHOLD else SCORE_FAIL
        if is_late:
            score = max(0, score - LATE_PENALTY)

        # Ensure row has enough columns
        while len(rows[row_idx]) <= col_index:
            rows[row_idx].append("")
        rows[row_idx][col_index] = str(score)
        graded_ids.add(sid)
        late_note = " [LATE -25]" if is_late else ""
        print(f"  Graded {sid}: {score} ({word_count} words){late_note}")

    # Set 0 for non-submitters (skip if excused)
    for sid, row_idx in id_to_row.items():
        if sid not in graded_ids:
            if is_excused(rows[row_idx], col_index):
                print(f"  Skipping {sid}: excused (EX)")
                continue
            while len(rows[row_idx]) <= col_index:
                rows[row_idx].append("")
            rows[row_idx][col_index] = "0"
            print(f"  No submission {sid}: 0")

    # Normalize row lengths to match header
    header_len = len(header)
    for row in rows:
        while len(row) < header_len:
            row.append("")

    # Output
    base = csv_path.stem
    out_path = output_dir / f"{base}_graded.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\nDone. Output saved to:\n  {out_path}")


if __name__ == "__main__":
    main()
