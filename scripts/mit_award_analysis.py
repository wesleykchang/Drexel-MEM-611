"""
Script: mit_award_analysis.py

Reads an Excel file (user provides path, e.g. ~/Desktop/file.xlsx), creates a pandas DataFrame,
finds MIT award numbers that share the same prefix (first 6 digits before '-') and have different
suffixes, then for each such prefix groups rows by PERSON_NAME and plots the total
AMOUNT_OBLIGATED_TO_DATE per PERSON_NAME. A separate bar plot is created for each prefix.

Usage:
    python scripts/mit_award_analysis.py --file ~/Desktop/your_file.xlsx

The script expects the following column names to exist (case-sensitive):
- 'MIT AWARD NUMBER' (format like '009000-123')
- 'PERSON_NAME'
- 'AMOUNT_OBLIGATED_TO_DATE'

"""

import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt


def load_excel(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    # Try default reader first; if pandas can't determine the engine, try common engines.
    try:
        return pd.read_excel(path)
    except ValueError as e:
        # pandas couldn't infer engine (common when file extension is unexpected or engine missing)
        last_err = e
        for engine in ("openpyxl", "xlrd", "pyxlsb"):
            try:
                return pd.read_excel(path, engine=engine)
            except Exception:
                # try next engine
                last_err = _
                continue
        # If we reach here, none of the engines worked. Raise a clear error with guidance.
        raise ValueError(
            f"Could not read Excel file '{path}'.\n"
            "Try installing 'openpyxl' (for .xlsx) or 'xlrd' (for .xls) and re-run.\n"
            f"Original error: {e}"
        ) from e


def normalize_award_prefix(df, col='MIT AWARD NUMBER'):
    """Extract the prefix (everything before the first dash) for each award number."""
    # Convert to string and strip
    s = df[col].astype(str).str.strip()
    # If there's a dash, take the left side; else take the first 6 characters as fallback
    prefix = s.str.split('-', n=1).str[0]
    # Optionally ensure prefix is at least 1 char
    return prefix


def find_multi_suffix_prefixes(prefix_series):
    """Return prefixes that appear with more than one distinct full award number suffix."""
    # Count distinct full award numbers per prefix
    # We'll assume prefix is everything before first dash
    return prefix_series.groupby(prefix_series).nunique().loc[lambda x: x > 1].index.tolist()


def analyze_and_plot(df, file_label='awards'):
    required = ['MIT AWARD NUMBER', 'PERSON_NAME', 'AMOUNT_OBLIGATED_TO_DATE']
    for r in required:
        if r not in df.columns:
            raise KeyError(f"Missing required column: {r}")

    df = df.copy()
    df['AWARD_PREFIX'] = normalize_award_prefix(df, 'MIT AWARD NUMBER')

    # Find prefixes that have multiple distinct full award numbers
    counts = df.groupby('AWARD_PREFIX')['MIT AWARD NUMBER'].nunique()
    multi_prefixes = counts[counts > 1].index.tolist()

    if not multi_prefixes:
        print("No award prefixes found with multiple suffixes.")
        return

    # For each prefix, group by PERSON_NAME and sum amounts
    for prefix in multi_prefixes:
        sub = df[df['AWARD_PREFIX'] == prefix]
        grouped = sub.groupby('PERSON_NAME', dropna=False)['AMOUNT_OBLIGATED_TO_DATE'].sum()
        grouped = grouped.sort_values(ascending=False)

        if grouped.empty:
            print(f"No data for prefix {prefix}")
            continue

        # Plot
        plt.figure(figsize=(8, 5))
        grouped.plot(kind='bar')
        plt.ylabel('Total AMOUNT_OBLIGATED_TO_DATE')
        plt.title(f'Prefix {prefix} - Total Obligated by Person')
        plt.tight_layout()
        outname = f"{file_label}_{prefix}_amounts.png"
        plt.savefig(outname, dpi=200)
        plt.close()
        print(f"Saved plot: {outname}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', required=True, help='Path to Excel (.xlsx) file')
    args = parser.parse_args()

    df = load_excel(os.path.expanduser(args.file))
    base = os.path.splitext(os.path.basename(args.file))[0]
    analyze_and_plot(df, file_label=base)


if __name__ == '__main__':
    main()
