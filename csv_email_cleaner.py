#!/usr/bin/env python3
"""
csv_email_cleaner.py
Usage:
  python csv_email_cleaner.py input.csv output.csv

What it does:
- Reads input CSV (keeps strings, is tolerant to quoting issues)
- Extracts valid email addresses from the Email column
- Splits rows with multiple emails into multiple rows (one email per row)
- Normalizes emails (lowercase) and removes duplicates (per Name+Email)
- Keeps rows with no valid email (Email will be empty)
- Writes cleaned CSV and prints summary
"""
import sys
import re
import pandas as pd

EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', re.IGNORECASE)

def extract_emails(cell):
    """Return list of valid email addresses found in the cell (lowercased, unique)."""
    if cell is None:
        return []
    s = str(cell).strip()

    # If field wrapped in extra quotes (common in broken CSVs), remove bounding quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()

    # Replace escaped double-quotes like "" -> "
    s = s.replace('""', '"')

    # Normalize separators to comma
    s = s.replace(';', ',')
    # Remove bracket characters that often surround junk
    s = re.sub(r'[\[\]\{\}\(\)]', ' ', s)

    # Find all email-like tokens using regex (more reliable than simple split)
    found = EMAIL_RE.findall(s)
    # Normalize and deduplicate preserving reasonable order
    seen = []
    for e in found:
        e_norm = e.strip().lower()
        if e_norm and e_norm not in seen:
            seen.append(e_norm)
    return seen

def main():
    if len(sys.argv) != 3:
        print("Usage: python csv_email_cleaner.py input.csv output.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read CSV: keep default_na=False so fields like "N/A" remain strings and are processed
    try:
        df = pd.read_csv(input_file, dtype=str, keep_default_na=False, encoding='utf-8')
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        sys.exit(1)

    if df.shape[0] == 0:
        print("Input CSV is empty. Nothing to do.")
        df.to_csv(output_file, index=False)
        return

    # Find email column case-insensitively
    email_col = None
    for c in df.columns:
        if c.strip().lower() == 'email':
            email_col = c
            break
    if email_col is None:
        print("No column named 'Email' found (case-insensitive). Columns found:", list(df.columns))
        sys.exit(1)

    # Extract emails per row
    df['_extracted_emails'] = df[email_col].apply(extract_emails)

    # Build output rows: one row per email, or empty email if none found
    out_rows = []
    total_found = 0
    for _, row in df.iterrows():
        emails = row['_extracted_emails']
        if emails:
            total_found += len(emails)
            for e in emails:
                new = row.to_dict()
                new[email_col] = e
                # remove helper col if present
                new.pop('_extracted_emails', None)
                out_rows.append(new)
        else:
            new = row.to_dict()
            new[email_col] = ''  # keep empty to indicate missing email
            new.pop('_extracted_emails', None)
            out_rows.append(new)

    out_df = pd.DataFrame(out_rows)

    # Drop exact duplicates (Name + Email); if Name not present, dedupe by Email only
    # Determine name column (case-insensitive)
    name_col = None
    for c in out_df.columns:
        if c.strip().lower() == 'name':
            name_col = c
            break

    if name_col:
        out_df = out_df.drop_duplicates(subset=[name_col, email_col])
    else:
        out_df = out_df.drop_duplicates(subset=[email_col])

    # Count unique non-empty emails
    unique_emails = out_df[email_col].replace('', pd.NA).dropna().nunique()

    # Save output
    try:
        out_df.to_csv(output_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error writing {output_file}: {e}")
        sys.exit(1)

    # Summary
    print("CSV email cleaning completed.")
    print(f"Input rows: {len(df)}")
    print(f"Total email tokens found (before dedupe): {total_found}")
    print(f"Unique non-empty emails in output: {unique_emails}")
    print(f"Output rows (including rows with empty Email): {len(out_df)}")
    print(f"Saved cleaned CSV to: {output_file}")

if __name__ == '__main__':
    main()
