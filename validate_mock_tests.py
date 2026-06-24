#!/usr/bin/env python3
"""
Comprehensive validation script for SSC CGL Mock Test CSV files.
Validates all 10 mock test files for format, content, and quality.
"""

import csv
import os
import sys
from collections import Counter

# Configuration
NUM_FILES = 10
EXPECTED_ROWS = 100
EXPECTED_PER_SUBJECT = 25
EXPECTED_HEADER = ["question", "option_a", "option_b", "option_c", "option_d", "correct", "explanation", "subject"]
VALID_CORRECT_VALUES = {"A", "B", "C", "D"}
VALID_SUBJECTS = {
    "General Intelligence and Reasoning",
    "General Awareness",
    "Quantitative Aptitude",
    "English Comprehension",
}
MIN_EXPLANATION_LENGTH = 10

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def validate_mock_tests():
    all_passed = True
    total_questions = 0
    subject_counts_global = Counter()
    all_questions = []  # (question_text, file_name) pairs for duplicate checking
    errors = []

    print("=" * 70)
    print("SSC CGL Mock Test Validation Report")
    print("=" * 70)
    print()

    # Check 1: All 10 files exist
    print("Check 1: Verifying all 10 files exist...")
    missing_files = []
    for i in range(1, NUM_FILES + 1):
        filepath = os.path.join(BASE_DIR, f"mock_test_{i}.csv")
        if not os.path.exists(filepath):
            missing_files.append(f"mock_test_{i}.csv")
    if missing_files:
        errors.append(f"Missing files: {', '.join(missing_files)}")
        print(f"  FAIL: Missing files: {', '.join(missing_files)}")
        all_passed = False
    else:
        print("  PASS: All 10 files exist.")
    print()

    # Validate each file
    for i in range(1, NUM_FILES + 1):
        filename = f"mock_test_{i}.csv"
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            continue

        print(f"--- Validating {filename} ---")
        file_errors = []
        file_questions = []

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            file_errors.append(f"Could not read file: {e}")
            errors.extend([f"{filename}: {err}" for err in file_errors])
            print(f"  FAIL: Could not read file: {e}")
            all_passed = False
            print()
            continue

        # Check 2: Header matches expected
        if len(rows) == 0:
            file_errors.append("File is empty")
        else:
            header = rows[0]
            if header != EXPECTED_HEADER:
                file_errors.append(
                    f"Header mismatch. Got: {header}, Expected: {EXPECTED_HEADER}"
                )

        # Check 3: Exactly 100 data rows
        data_rows = rows[1:] if len(rows) > 0 else []
        if len(data_rows) != EXPECTED_ROWS:
            file_errors.append(
                f"Expected {EXPECTED_ROWS} data rows, got {len(data_rows)}"
            )

        # Validate each row
        subject_counts = Counter()
        for row_idx, row in enumerate(data_rows, start=2):
            row_label = f"Row {row_idx}"

            # Check column count
            if len(row) != 8:
                file_errors.append(
                    f"{row_label}: Expected 8 columns, got {len(row)}"
                )
                continue

            question, opt_a, opt_b, opt_c, opt_d, correct, explanation, subject = row

            # Check 6: No empty/blank fields
            for col_idx, (field_name, value) in enumerate(
                zip(EXPECTED_HEADER, row)
            ):
                if not value or not value.strip():
                    file_errors.append(
                        f"{row_label}: Empty field '{field_name}'"
                    )

            # Check 5: correct column is A, B, C, or D
            if correct.strip() not in VALID_CORRECT_VALUES:
                file_errors.append(
                    f"{row_label}: Invalid correct value '{correct}'. Must be A, B, C, or D."
                )

            # Check 7: subject values are valid
            if subject.strip() not in VALID_SUBJECTS:
                file_errors.append(
                    f"{row_label}: Invalid subject '{subject}'"
                )
            else:
                subject_counts[subject.strip()] += 1

            # Check 9: Explanation length
            if len(explanation.strip()) < MIN_EXPLANATION_LENGTH:
                file_errors.append(
                    f"{row_label}: Explanation too short ({len(explanation.strip())} chars): '{explanation.strip()[:50]}...'"
                )

            # Collect questions for duplicate check
            if question.strip():
                file_questions.append(question.strip())

        # Check 4: Exactly 25 questions per subject
        for subj in VALID_SUBJECTS:
            count = subject_counts.get(subj, 0)
            if count != EXPECTED_PER_SUBJECT:
                file_errors.append(
                    f"Subject '{subj}': Expected {EXPECTED_PER_SUBJECT} questions, got {count}"
                )

        # Accumulate totals
        total_questions += len(data_rows)
        for subj, count in subject_counts.items():
            subject_counts_global[subj] += count

        # Store questions for cross-file duplicate check
        for q in file_questions:
            all_questions.append((q, filename))

        # Report per-file results
        if file_errors:
            all_passed = False
            print(f"  FAIL: {len(file_errors)} error(s) found:")
            for err in file_errors[:10]:  # Show first 10
                print(f"    - {err}")
            if len(file_errors) > 10:
                print(f"    ... and {len(file_errors) - 10} more errors")
            errors.extend([f"{filename}: {err}" for err in file_errors])
        else:
            print(f"  PASS: All checks passed. ({len(data_rows)} questions, 25 per subject)")
        print()

    # Check 8: Duplicate questions across ALL files
    print("--- Cross-file Duplicate Check ---")
    question_locations = {}
    duplicates = []
    for question_text, filename in all_questions:
        if question_text in question_locations:
            duplicates.append(
                (question_text[:80], question_locations[question_text], filename)
            )
        else:
            question_locations[question_text] = filename

    if duplicates:
        all_passed = False
        print(f"  FAIL: {len(duplicates)} duplicate question(s) found:")
        for q_text, file1, file2 in duplicates[:20]:
            print(f"    - \"{q_text}...\" in {file1} and {file2}")
        if len(duplicates) > 20:
            print(f"    ... and {len(duplicates) - 20} more duplicates")
        errors.append(f"{len(duplicates)} duplicate questions found across files")
    else:
        print("  PASS: No duplicate questions found across all files.")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files validated: {NUM_FILES}")
    print(f"Total questions: {total_questions}")
    print(f"Expected total questions: {NUM_FILES * EXPECTED_ROWS}")
    print()
    print("Questions per subject (across all tests):")
    for subj in sorted(VALID_SUBJECTS):
        count = subject_counts_global.get(subj, 0)
        expected = NUM_FILES * EXPECTED_PER_SUBJECT
        status = "OK" if count == expected else "MISMATCH"
        print(f"  {subj}: {count} ({status}, expected {expected})")
    print()

    if all_passed:
        print("RESULT: PASS - All validations passed!")
        print(f"  - All {NUM_FILES} files exist")
        print(f"  - All files have exactly {EXPECTED_ROWS} questions")
        print(f"  - All files have {EXPECTED_PER_SUBJECT} questions per subject")
        print(f"  - All correct answers are A/B/C/D")
        print(f"  - No empty fields found")
        print(f"  - All subjects are valid")
        print(f"  - No duplicate questions across files")
        print(f"  - All explanations are at least {MIN_EXPLANATION_LENGTH} characters")
    else:
        print(f"RESULT: FAIL - {len(errors)} error(s) found.")
        print("Errors:")
        for err in errors[:30]:
            print(f"  - {err}")
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more errors")

    print("=" * 70)
    return all_passed


if __name__ == "__main__":
    success = validate_mock_tests()
    sys.exit(0 if success else 1)
