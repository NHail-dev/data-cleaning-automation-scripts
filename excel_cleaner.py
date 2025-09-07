import pandas as pd
import sys

def clean_excel(input_file, output_file):
    df = pd.read_excel(input_file)

    # Example cleaning steps
    drop_cols = ['Notes', 'Temp']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    if 'Price' in df.columns:
        df['Price'] = df['Price'].round(2)

    if 'Week' in df.columns:
        df = df[df['Week'] == '2025-W35']

    df.to_excel(output_file, index=False)
    print(f"Cleaned file saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python excel_cleaner.py input.xlsx output.xlsx")
    else:
        clean_excel(sys.argv[1], sys.argv[2])
