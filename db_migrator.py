import pandas as pd
from sqlalchemy import create_engine
import sys

def migrate_csv_to_db(input_file, db_url, table_name):
    df = pd.read_csv(input_file)

    # Drop duplicates and clean column names
    df = df.drop_duplicates()
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    engine = create_engine(db_url)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Data migrated into {table_name} at {db_url}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python db_migrator.py input.csv db_url table_name")
        print("Example: python db_migrator.py data.csv sqlite:///test.db mytable")
    else:
        migrate_csv_to_db(sys.argv[1], sys.argv[2], sys.argv[3])
